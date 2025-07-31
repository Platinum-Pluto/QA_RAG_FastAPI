from fastapi import FastAPI, UploadFile, File, HTTPException
from uuid import uuid4
import os
from rag import gen_ans

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


app = FastAPI()

files = []


@app.get("/")
async def root():
    return {"message": "WELCOME TO THE QA RAG FastAPI!!!"}


@app.post("/query")
async def query_rag(query, *items):
    try:
        global files
        files = list(items)
        response, context = gen_ans(query)
        return {"Context":context, "Response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_id = str(uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        return {
            "message": "File uploaded successfully.",
            "file_id": file_id,
            "filename": file.filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
