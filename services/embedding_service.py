# services/embedding_service.py

import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def generate_embedding(text: str) -> list[float]:
    return model.encode(text).tolist()


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    return model.encode(texts).tolist()
