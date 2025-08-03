from fastapi import FastAPI, UploadFile, File
from uuid import uuid4
import os
from typing import List, Optional
from rag import PlatinumPipeline, query_image_base64
from pathlib import Path
from pydantic import BaseModel
import re

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

def clean_uploads():
    folder = Path(UPLOAD_DIR)
    for file in folder.iterdir():
        if file.is_file():
            file.unlink()



class Query(BaseModel):
    query: str
    base64_image_url: Optional[str] = None


def get_icon_for_file(filename: str) -> str:
    ext = filename.split(".")[-1].lower()
    return {
        "pdf": "📕",
        "docx": "📘",
        "txt": "📄",
        "csv": "📊",
        "png": "🖼️",
        "jpg": "🖼️",
        "jpeg": "🖼️",
        "xlsx": "📊",
        "json": "🗂️",
        "sqlite": "🗃️",
        "db": "🗃️",
        "md": "📓"
    }.get(ext, "📁") 


def source_infos(context):
    source = []
    for c in context:
        file_path = c.metadata.get("file_path", "unknown")
        file_name = re.sub(r'^.*?_', '', os.path.basename(file_path))
        icon = get_icon_for_file(file_name)
        page = c.metadata.get("page", 0) + 1
        source.append(f"{icon} Page {page} of {file_name}")
    return source


@app.get("/")
async def root():
    return {"message": "WELCOME TO THE QA RAG FastAPI!!!"}


@app.post("/query")
async def query_rag(request: Query):

    if request.base64_image_url:
        try:
            response = query_image_base64(request.base64_image_url, request.query)
            return {"Context": [""], "Response": response, "Source Info": f'🖼️ {request.base64_image_url}'}
        except Exception as e:
            return{"Context": [], "Response": f"Failed to process image: {str(e)}", "Source Info": []}
    try:    
        rag = PlatinumPipeline()
        response, context = rag.gen_ans(request.query)
        formatted_contexts = [c.page_content for c in context]
        source = []
        source = source_infos(context)
        clean_uploads()
        #print(response)
        return {"Context":formatted_contexts, "Response": response, "Source Info": source}
    except Exception as e:
        return{"Context": [], "Response": f"Failed to process image: {str(e)}", "Source Info": []}
    

@app.post("/upload")
async def upload_file(file: List[UploadFile] = File(...)):
    names = []
    ids = []
    global files
    for f in file:
        file_id = str(uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{f.filename}")
        names.append(f.filename)
        ids.append(file_id)        
        with open(file_path, "wb") as buffer:
            content = await f.read()
            buffer.write(content)
    
    return {
        "message": "File uploaded successfully.",
        "file_id": ids,
        "filename": names
    }



