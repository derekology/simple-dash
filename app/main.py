import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.utils.detector import detect_and_parse
from app.models import ParseError, InvalidCampaignError, EmptyReportError, UnsupportedFormatError, InvalidFileError
from typing import List, Dict
from datetime import datetime

# Configuration from environment variables
DEV = os.getenv("DEV", "False").lower() in ("true", "1", "yes")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # Default: 10MB
MAX_FILES = int(os.getenv("MAX_FILES", "12"))  # Default: 12

# Rate limiter that works with Cloudflare proxied requests
def get_real_ip(request: Request) -> str:
    """Get real IP from Cloudflare headers, fallback to remote address"""
    forwarded_for = request.headers.get("CF-Connecting-IP")
    if forwarded_for:
        return forwarded_for
    
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    return get_remote_address(request)

limiter = Limiter(key_func=get_real_ip)

app = FastAPI(
    title="Simple Dash",
    description="Email campaign analytics tool",
    version="1.0.0",
    docs_url=None,  # Disable /docs
    redoc_url=None,  # Disable /redoc
    openapi_url=None  # Disable /openapi.json
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

allowed_origins = ["*"] if DEV else [
    "https://simpledash.wooprojects.com/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def get_file_modified_time(file: UploadFile) -> datetime:
    """Get file modified time from upload metadata if available, otherwise use current time."""
    # FastAPI UploadFile doesn't provide file modification time
    # We'll use upload order as a proxy (later files override earlier ones)
    return datetime.now()


@app.post("/parse")
@limiter.limit("10/minute")
async def parse_report(request: Request, files: List[UploadFile] = File(...)):
    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum {MAX_FILES} files allowed per upload."
        )
    
    total_size = 0
    file_contents = []
    
    for file in files:
        contents = await file.read()
        total_size += len(contents)
        file_contents.append((file.filename, contents))
        
        await file.seek(0)
    
    max_total_size = MAX_FILE_SIZE * MAX_FILES
    if total_size > max_total_size:
        raise HTTPException(
            status_code=413,
            detail=f"Total upload size exceeds maximum allowed ({max_total_size // (1024 * 1024)}MB)"
        )
    
    results = []
    errors = []
    campaigns_by_id: Dict[str, dict] = {}
    file_index = 0
    
    for filename, contents in file_contents:
        if not filename.lower().endswith(".csv"):
            errors.append({
                "filename": filename,
                "error": "Only CSV files supported"
            })
            continue

        if len(contents) > MAX_FILE_SIZE:
            errors.append({
                "filename": filename,
                "error": f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)}MB"
            })
            continue
        
        try:
            text = contents.decode("utf-8", errors="ignore")
        except Exception as e:
            errors.append({
                "filename": filename,
                "error": f"Failed to decode file: {str(e)}"
            })
            continue

        try:
            campaigns = detect_and_parse(text)
            
            if not campaigns:
                errors.append({
                    "filename": filename,
                    "error": "No campaigns found in file"
                })
                continue
            
            for campaign in campaigns:
                if not campaign.has_meaningful_data():
                    continue
                
                unique_id = campaign.unique_id
                campaign_dict = campaign.to_dict()
                
                if unique_id:
                    if unique_id not in campaigns_by_id or file_index > campaigns_by_id[unique_id].get("_file_index", -1):
                        campaign_dict["_file_index"] = file_index
                        campaigns_by_id[unique_id] = campaign_dict
                else:
                    results.append({
                        "filename": filename,
                        "data": {"campaign": campaign_dict}
                    })
            
            file_index += 1
            
        except EmptyReportError as e:
            errors.append({
                "filename": filename,
                "error": f"Empty report: {e.message}"
            })
        except UnsupportedFormatError as e:
            errors.append({
                "filename": filename,
                "error": f"Unsupported format: {e.message}"
            })
        except InvalidCampaignError as e:
            errors.append({
                "filename": filename,
                "error": f"Invalid campaign: {e.message}"
            })
        except ParseError as e:
            errors.append({
                "filename": filename,
                "error": f"Parse error: {e.message}"
            })
        except Exception as e:
            errors.append({
                "filename": filename,
                "error": f"Failed to parse: {str(e)}"
            })
    
    for unique_id, campaign in campaigns_by_id.items():
        campaign.pop("_file_index", None)
        results.append({
            "filename": "deduplicated",
            "data": {"campaign": campaign}
        })
    
    return {
        "results": results,
        "errors": errors
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and monitoring"""
    return {
        "status": "healthy",
        "max_file_size": MAX_FILE_SIZE,
        "max_files": MAX_FILES
    }


if os.path.exists("frontend/dist"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")
    
    @app.get("/favicon.ico")
    async def serve_favicon():
        dist_favicon = "frontend/dist/favicon.ico"
        if os.path.exists(dist_favicon):
            return FileResponse(dist_favicon)
        
        public_favicon = "frontend/public/favicon.ico"
        if os.path.exists(public_favicon):
            return FileResponse(public_favicon)
        raise HTTPException(status_code=404, detail="Favicon not found")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("parse"):
            raise HTTPException(status_code=404, detail="Not found")
        
        return FileResponse("frontend/dist/index.html")
