import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.parsers.detector import detect_and_parse
from typing import List, Dict
from datetime import datetime

DEV = True
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILES = 12

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_file_modified_time(file: UploadFile) -> datetime:
    """Get file modified time from upload metadata if available, otherwise use current time."""
    # FastAPI UploadFile doesn't provide file modification time
    # We'll use upload order as a proxy (later files override earlier ones)
    return datetime.now()


@app.post("/parse")
async def parse_report(files: List[UploadFile] = File(...)):
    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum {MAX_FILES} files allowed per upload."
        )
    
    results = []
    errors = []
    campaigns_by_id: Dict[str, dict] = {}  # For deduplication
    file_index = 0  # Track upload order
    
    for file in files:
        if not file.filename.lower().endswith(".csv"):
            errors.append({
                "filename": file.filename,
                "error": "Only CSV files supported"
            })
            continue

        contents = await file.read()
        
        if len(contents) > MAX_FILE_SIZE:
            errors.append({
                "filename": file.filename,
                "error": f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)}MB"
            })
            continue
        
        text = contents.decode("utf-8", errors="ignore")

        try:
            result = detect_and_parse(text)
            
            # Handle both single campaign and multiple campaigns
            if "campaign" in result:
                # Single campaign (MailerLite Classic)
                campaign = result["campaign"]
                unique_id = campaign.get("unique_id")
                
                if unique_id:
                    # Store with file index for deduplication
                    if unique_id not in campaigns_by_id or file_index > campaigns_by_id[unique_id].get("_file_index", -1):
                        campaign["_file_index"] = file_index
                        campaigns_by_id[unique_id] = campaign
                else:
                    # No unique ID, add directly
                    results.append({
                        "filename": file.filename,
                        "data": {"campaign": campaign}
                    })
                    
            elif "campaigns" in result:
                # Multiple campaigns (MailChimp)
                for campaign in result["campaigns"]:
                    unique_id = campaign.get("unique_id")
                    
                    if unique_id:
                        # Store with file index for deduplication
                        if unique_id not in campaigns_by_id or file_index > campaigns_by_id[unique_id].get("_file_index", -1):
                            campaign["_file_index"] = file_index
                            campaigns_by_id[unique_id] = campaign
                    else:
                        # No unique ID, add directly
                        results.append({
                            "filename": file.filename,
                            "data": {"campaign": campaign}
                        })
            
            file_index += 1
            
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    # Add deduplicated campaigns to results
    for unique_id, campaign in campaigns_by_id.items():
        # Remove internal tracking field
        campaign.pop("_file_index", None)
        results.append({
            "filename": "deduplicated",
            "data": {"campaign": campaign}
        })
    
    return {
        "results": results,
        "errors": errors
    }

if os.path.exists("frontend/dist"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")
    
    @app.get("/favicon.ico")
    async def serve_favicon():
        favicon_path = "frontend/public/favicon.ico"
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path)
        raise HTTPException(status_code=404, detail="Favicon not found")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("parse"):
            raise HTTPException(status_code=404, detail="Not found")
        
        return FileResponse("frontend/dist/index.html")
