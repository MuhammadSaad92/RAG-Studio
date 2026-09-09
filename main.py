from fastapi import FastAPI, HTTPException
from pinecone import Pinecone
from dotenv import load_dotenv
import os

from services.pipeline_service import ingest_pdf, answer_question

load_dotenv()

app = FastAPI()

pinecone = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)


@app.get("/pinecone-test")
def pinecone_test():
    indexes = pinecone.list_indexes()

    return {
        "indexes": [index.name for index in indexes]
    }
    
@app.get("/")
def root():
    return{"message": "RAG Backend is running..."}


@app.post("/ingest")
def ingest():
    """Extract, chunk, embed and upload the PDF into Pinecone."""
    try:
        result = ingest_pdf()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")

    return {"status": "ok", **result}


@app.get("/query")
def query(q: str, top_k: int = 4):
    """Answer a question using RAG over the ingested PDF."""
    if not q.strip():
        raise HTTPException(status_code=422, detail="Query 'q' must not be empty.")

    try:
        return answer_question(q, top_k=top_k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Query failed: {exc}")


