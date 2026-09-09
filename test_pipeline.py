# test_pipeline.py

from services.pdf_service import extract_text_from_pdf
from services.chunk_service import chunk_text
from services.embedding_service import generate_embeddings
from services.pinecone_service import upsert_embeddings

PDF_PATH = "data/company_employee_data.pdf"


# 1. Extract PDF text
text = extract_text_from_pdf(PDF_PATH)

print("Extracted characters:", len(text))


# 2. Chunk text
chunks = chunk_text(text)

print("Total chunks:", len(chunks))


# 3. Generate embeddings
embeddings = generate_embeddings(chunks)

print("Total embeddings:", len(embeddings))


# 4. Inspect embeddings
for i, embedding in enumerate(embeddings):
    print(f"\n--- Embedding {i + 1} ---")
    print("Vector dimensions:", len(embedding))
    print("First 5 values:", embedding[:5])


# 5. Upload to Pinecone
uploaded = upsert_embeddings(chunks, embeddings)

print("Uploaded to Pinecone:", uploaded)