import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.utils.detector import detect_and_parse
from typing import List, Dict
from datetime import datetime

# Configuration from environment variables
DEV = os.getenv("DEV", "False").lower() in ("true", "1", "yes")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # Default: 10MB
MAX_FILES = int(os.getenv("MAX_FILES", "12"))  # Default: 12

app = FastAPI(title="Simple Dash", description="Email campaign analytics tool", version="1.0.0")

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
        
        try:
            text = contents.decode("utf-8", errors="ignore")
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": f"Failed to decode file: {str(e)}"
            })
            continue

        try:
            result = detect_and_parse(text)
            
            # Validate that parsing returned actual data
            if not result:
                errors.append({
                    "filename": file.filename,
                    "error": "Failed to parse: No data returned from parser"
                })
                continue
            
            # Handle both single campaign and multiple campaigns
            print(result)
            # if "campaign" in result:
            #     # Single campaign (MailerLite Classic)
            #     campaign = result["campaign"]
                
            #     if not campaign:
            #         errors.append({
            #             "filename": file.filename,
            #             "error": "Failed to parse: Empty campaign data"
            #         })
            #         continue
                
            #     # Validate that campaign has at least some meaningful data
            #     # Check if key fields have actual values (not all None)
            #     has_data = any([
            #         campaign.get("subject"),
            #         campaign.get("delivered"),
            #         campaign.get("opens"),
            #         campaign.get("clicks"),
            #         campaign.get("sent_at")
            #     ])
                
            #     if not has_data:
            #         errors.append({
            #             "filename": file.filename,
            #             "error": "Failed to parse: No valid campaign data found in file"
            #         })
            #         continue
                
            #     unique_id = campaign.get("unique_id")
                
            #     if unique_id:
            #         # Store with file index for deduplication
            #         if unique_id not in campaigns_by_id or file_index > campaigns_by_id[unique_id].get("_file_index", -1):
            #             campaign["_file_index"] = file_index
            #             campaigns_by_id[unique_id] = campaign
            #     else:
            #         # No unique ID, add directly
            #         results.append({
            #             "filename": file.filename,
            #             "data": {"campaign": campaign}
            #         })
                    
            if "campaigns" in result:
                # Multiple campaigns (MailChimp)
                campaigns = result["campaigns"]
                
                if not campaigns or len(campaigns) == 0:
                    errors.append({
                        "filename": file.filename,
                        "error": "Failed to parse: No campaigns found in file"
                    })
                    continue
                
                # Validate each campaign has meaningful data
                valid_campaigns = []
                for campaign in campaigns:
                    has_data = any([
                        campaign.get("subject"),
                        campaign.get("delivered"),
                        campaign.get("opens"),
                        campaign.get("clicks"),
                        campaign.get("sent_at")
                    ])
                    if has_data:
                        valid_campaigns.append(campaign)
                
                if len(valid_campaigns) == 0:
                    errors.append({
                        "filename": file.filename,
                        "error": "Failed to parse: No valid campaign data found in file"
                    })
                    continue
                
                for campaign in valid_campaigns:
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
                        # # No unique ID, add to failed parses
                        # errors.append({
                        #     "filename": file.filename,
                        #     "error": "Failed to parse: Could not generate unique_id"
                        # })
            else:
                # Neither 'campaign' nor 'campaigns' in result
                errors.append({
                    "filename": file.filename,
                    "error": "Failed to parse: Unknown data format returned"
                })
                continue
            
            file_index += 1
            
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": f"Failed to parse: {str(e)}"
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
