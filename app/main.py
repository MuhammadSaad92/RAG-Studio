from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pinecone import Pinecone
from dotenv import load_dotenv
import os

from services.pipeline_service import ingest_pdf, answer_question

load_dotenv()

app = FastAPI()

pinecone = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

if not os.getenv("VERCEL"):
    from fastapi.staticfiles import StaticFiles
    static_dir = "public/static" if os.path.exists("public/static") else "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/pinecone-test")
def pinecone_test():
    indexes = pinecone.list_indexes()
    return {
        "indexes": [index.name for index in indexes]
    }


@app.get("/")
def root():
    if not os.getenv("VERCEL"):
        html_path = "public/index.html" if os.path.exists("public/index.html") else "static/index.html"
        if os.path.exists(html_path):
            return FileResponse(html_path)
    return {"message": "RAG Studio API is running"}


@app.post("/ingest")
def ingest():
    try:
        result = ingest_pdf()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")
    return {"status": "ok", **result}


@app.get("/query")
def query(q: str, top_k: int = 4):
    if not q.strip():
        raise HTTPException(status_code=422, detail="Query 'q' must not be empty.")
    try:
        return answer_question(q, top_k=top_k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Query failed: {exc}")
