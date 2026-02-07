import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.parsers.detector import detect_and_parse
from typing import List

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

@app.post("/parse")
async def parse_report(files: List[UploadFile] = File(...)):
    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum {MAX_FILES} files allowed per upload."
        )
    
    results = []
    errors = []
    
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
            results.append({
                "filename": file.filename,
                "data": result
            })
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
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
