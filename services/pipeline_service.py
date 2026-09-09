# services/pipeline_service.py

import os

from services.pdf_service import extract_text_from_pdf
from services.chunk_service import chunk_text
from services.embedding_service import generate_embedding, generate_embeddings
from services.pinecone_service import (
    delete_all_vectors,
    query_index,
    upsert_embeddings
)
from services.llm_service import generate_answer

PDF_PATH = "data/company_employee_data.pdf"

# Below this similarity score, the question is considered off-topic and the
# slow LLM call is skipped entirely. Measured on this doc: related questions
# score ~0.25-0.51, unrelated ones ~-0.03-0.1, so 0.15 sits safely in between.
# Questions above the gate but not answered by the doc are handled by the LLM
# prompt ("say you don't know if not in context").
RELEVANCE_THRESHOLD = 0.15

OFF_TOPIC_ANSWER = (
    "I can only answer questions about the ingested company employee policy "
    "document. Please ask something related to it."
)


def ingest_pdf(pdf_path: str = PDF_PATH) -> dict:
    # 1. Extract text from the PDF
    text = extract_text_from_pdf(pdf_path)

    # 2. Chunk the text
    chunks = chunk_text(text)

    # 3. Generate embeddings for all chunks
    embeddings = generate_embeddings(chunks)

    # 4. Clear old vectors, then upload the fresh ones
    delete_all_vectors()
    uploaded = upsert_embeddings(
        chunks,
        embeddings,
        source=os.path.basename(pdf_path)
    )

    return {
        "source": os.path.basename(pdf_path),
        "characters": len(text),
        "chunks": len(chunks),
        "uploaded": uploaded
    }


def answer_question(question: str, top_k: int = 4,
                    min_relevance: float = RELEVANCE_THRESHOLD) -> dict:
    # 1. Embed the question
    question_embedding = generate_embedding(question)

    # 2. Retrieve the most relevant chunks from Pinecone
    matches = query_index(question_embedding, top_k=top_k)

    # 3. If nothing in the index is relevant, skip the LLM call entirely —
    #    this keeps off-topic questions fast.
    top_score = matches[0]["score"] if matches else 0.0

    if top_score < min_relevance:
        return {
            "question": question,
            "answer": OFF_TOPIC_ANSWER,
            "sources": [],
            "relevant": False,
            "top_score": top_score
        }

    # 4. Generate an answer from the retrieved context
    contexts = [match["text"] for match in matches]
    answer = generate_answer(question, contexts)

    sources = [
        {
            "source": match["source"],
            "score": match["score"]
        }
        for match in matches
    ]

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "relevant": True,
        "top_score": top_score
    }
