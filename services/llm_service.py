# services/llm_service.py

import os

from google import genai
from dotenv import load_dotenv

load_dotenv()

client = None


def _get_client():
    """Create the Gemini client lazily so the app can start (and /ingest works)
    even before GEMINI_API_KEY is configured."""
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


MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

PROMPT_TEMPLATE = """You are a helpful assistant that answers questions about company \
employee policies. Use ONLY the context below to answer. If the answer is not \
contained in the context, say you don't know instead of guessing.

Context:
{context}

Question: {question}

Answer:"""


def generate_answer(question: str, contexts: list[str]) -> str:
    context_text = "\n\n---\n\n".join(contexts)

    response = _get_client().models.generate_content(
        model=MODEL_NAME,
        contents=PROMPT_TEMPLATE.format(
            context=context_text,
            question=question
        )
    )

    return response.text
