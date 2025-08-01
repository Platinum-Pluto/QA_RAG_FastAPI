from fastapi import FastAPI, UploadFile, File
from uuid import uuid4
import os
from typing import List
from rag import gen_ans
from pathlib import Path

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()
files = []

def clean_uploads():
    folder = Path(UPLOAD_DIR)
    for file in folder.iterdir():
        if file.is_file():
            file.unlink()

def list_files():
    global files
    for filename in os.listdir(UPLOAD_DIR):
        if os.path.isfile(os.path.join(UPLOAD_DIR, filename)):
            files.append(filename)


@app.get("/")
async def root():
    return {"message": "WELCOME TO THE QA RAG FastAPI!!!"}

@app.post("/query")
async def query_rag(query, file: List[UploadFile] = File(...)):
    global files
    if not file and os.listdir(UPLOAD_DIR):
        list_files()
        response, context = gen_ans(query)
        files.clear()
        clean_uploads()
        return {"Context":context, "Response": response}
    
    elif file:
        for f in file:
            path = os.path.join(UPLOAD_DIR, f.filename)
            files.append(path)
        response, context = gen_ans(query)
        files.clear()
        clean_uploads()
        return {"Context":context, "Response": response}
    
    else:
        return {"message": "No files were uploaded"}


@app.post("/upload")
async def upload_file(file: List[UploadFile] = File(...)):
    names = []
    ids = []
    global files
    for f in file:
        file_id = str(uuid4())
        path = os.path.join(UPLOAD_DIR, f"{file_id}_{f.filename}")
        names.append(f.filename)
        ids.append(file_id)
        files.append(path)
    """        
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    """
    return {
        "message": "File uploaded successfully.",
        "file_id": ids,
        "filename": names
    }