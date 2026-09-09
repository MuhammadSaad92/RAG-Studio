# app/services/chunk_service.py

def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150
) -> list[str]:

    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.")

    chunks = []

    start = 0
    step = chunk_size - overlap

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += step

    return chunks