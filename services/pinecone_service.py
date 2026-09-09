# app/services/pinecone_service.py

import os
import hashlib

from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

index = pc.Index("rag-demo")


def list_indexes():
    return pc.list_indexes()


def upsert_embeddings(chunks, embeddings, source: str = "company_employee_data.pdf") -> int:
    vectors = []

    for chunk, embedding in zip(chunks, embeddings):
        # Hash-based ID: identical chunks overwrite themselves on re-ingest
        # instead of piling up duplicates in the index.
        chunk_id = hashlib.md5(chunk.encode("utf-8")).hexdigest()

        vectors.append({
            "id": chunk_id,
            "values": embedding,
            "metadata": {
                "text": chunk,
                "source": source
            }
        })

    index.upsert(vectors=vectors)

    return len(vectors)


def delete_all_vectors() -> None:
    """Clear the index so a re-ingest never leaves stale vectors behind."""
    index.delete(delete_all=True)


def query_index(query_embedding: list[float], top_k: int = 4) -> list[dict]:
    result = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    matches = []

    for match in result.matches:
        metadata = match.metadata or {}

        matches.append({
            "id": match.id,
            "score": match.score,
            "text": metadata.get("text", ""),
            "source": metadata.get("source", "")
        })

    return matches