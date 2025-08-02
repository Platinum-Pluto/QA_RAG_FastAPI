from fastapi import FastAPI, UploadFile, File
from uuid import uuid4
import os
from typing import List
from rag import PlatinumPipeline
from pathlib import Path

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

def clean_uploads():
    folder = Path(UPLOAD_DIR)
    for file in folder.iterdir():
        if file.is_file():
            file.unlink()


@app.get("/")
async def root():
    return {"message": "WELCOME TO THE QA RAG FastAPI!!!"}

@app.post("/query")
async def query_rag(query, file: List[UploadFile] = File(...)):
    if not file and os.listdir(UPLOAD_DIR):
        rag = PlatinumPipeline()
        response, context = rag.gen_ans(query)
        clean_uploads()
        return {"Context":context, "Response": response}
    
    elif file:
        for f in file:
            file_path = os.path.join(UPLOAD_DIR, f.filename)
            with open(file_path, "wb") as buffer:
                content = await f.read()
                buffer.write(content)
        rag = PlatinumPipeline()
        response, context = rag.gen_ans(query)
        formatted_contexts = [c.page_content for c in context]
        source = [f"Page {c.metadata.get('page', 0) + 1} of {os.path.basename(c.metadata.get('file_path', 'unknown'))}" for c in context]
        clean_uploads()
        return {"Context":formatted_contexts, "Response": response, "Source Info": source}
    
    else:
        return {"message": "No files were uploaded"}


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