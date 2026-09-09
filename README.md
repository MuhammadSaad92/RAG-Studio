RAG Studio is an end-to-end Retrieval-Augmented Generation (RAG) application that turns any PDF document into an intelligent, searchable knowledge base. Built with Streamlit, it lets users ask natural-language questions about an employee policy handbook and receive accurate, context-grounded answers — each backed by cited source chunks and relevance scores. Documents are parsed with pypdf, split into semantic chunks, embedded with all-MiniLM-L6-v2, and indexed in Pinecone; at query time, the most relevant chunks are retrieved and passed to Google Gemini to generate precise answers.

📖 Full description
What it does
RAG Studio solves a real problem: company policy documents are long, and nobody reads them. Instead of scrolling through 40 pages of PDF to find the remote-work policy or vacation entitlement, users simply ask — "How many vacation days do I get?" — and get an instant, accurate answer traced back to the exact document section it came from.

How it works (Architecture)
text

┌──────────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│    pypdf     │ →   │  Chunking   │ →   │ all-MiniLM-  │ →   │  Pinecone   │
│  PDF extract │     │ (semantic)  │     │ L6-v2 embed  │     │ (vector DB) │
└──────────────┘     └─────────────┘     └──────────────┘     └─────────────┘
                                                                      ↑ index
┌──────────────┐     ┌──────────────────────────────────────────────┐ │
│   Gemini     │ ←   │           User Question                      │─┘
│  (generate)  │     │      ↓ embed → similarity search (top-K)     │
└──────────────┘     └──────────────────────────────────────────────┘
        ↓
  Grounded answer + cited sources + relevance scores
Ingestion pipeline: Extract text from PDF → split into overlapping chunks → convert each chunk into a 384-dimensional vector embedding → upsert into Pinecone.

Query pipeline: Embed the user's question → retrieve top-K most similar chunks via cosine similarity → feed them as context to Gemini → return the generated answer with full source attribution.

Key features
💬 Conversational chat UI — persistent session history with a premium dark glassmorphism interface
📄 Source citations — every answer displays the retrieved chunks with similarity scores, so users can verify claims
🎛️ Adjustable retrieval depth — top-K slider to balance context breadth vs. precision
🔄 One-click re-ingestion — rebuild the vector index anytime the source document changes
✅ Grounded answers — responses are generated only from indexed document content, reducing hallucination
🧹 Session controls — clear conversation, live index status, error handling with persisted state
Tech stack
Layer
Technology
Frontend	Streamlit (custom CSS, glassmorphism UI)
PDF parsing	pypdf
Embeddings	sentence-transformers — all-MiniLM-L6-v2 (384-dim)
Vector database	Pinecone (serverless)
LLM	Google Gemini API
Language	Python 3.10+
