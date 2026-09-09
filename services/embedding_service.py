import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = None


def _get_client():
    global client
    if client is None:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Get a free key at https://aistudio.google.com "
                "and add it to your .env file."
            )
        client = genai.Client(api_key=api_key)
    return client


EMBEDDING_MODEL = "models/text-embedding-004"


def generate_embedding(text: str) -> list[float]:
    result = _get_client().models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text
    )
    return result.embeddings[0].values


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    result = _get_client().models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts
    )
    return [emb.values for emb in result.embeddings]
