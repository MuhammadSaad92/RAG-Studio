# 🧠 RAG Studio — Employee Policy Q&A

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![HTML/CSS/JS](https://img.shields.io/badge/Frontend-HTML%2FCSS%2FJS-purple)](https://developer.mozilla.org)
[![Pinecone](https://img.shields.io/badge/Pinecone-Serverless-green)](https://pinecone.io)
[![Gemini](https://img.shields.io/badge/Gemini-API-orange)](https://deepmind.google/technologies/gemini/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

An AI-powered Q&A assistant that answers questions about company policy documents using **RAG (Retrieval-Augmented Generation)** — grounded, cited answers via Pinecone vector search + Google Gemini.

---

## 🎯 What it does

Company policy documents are long — and nobody reads them. Instead of scrolling through 40 pages of PDF to find the remote‑work policy or vacation entitlement, users simply ask:

> *"How many vacation days do I get?"*

…and get an **instant, accurate answer** traced back to the exact document section it came from — with source chunks and relevance scores shown for verification.

---

## 🏗️ Architecture

| Stage        | Detail                                                                                      |
|--------------|----------------------------------------------------------------------------------------------|
| **Ingestion**| Extract text from PDF → split into overlapping chunks → embed (384‑dim) → upsert to Pinecone |
| **Query**    | Embed question → retrieve top‑K chunks (cosine similarity) → pass as context to Gemini → generate answer |

---

## ✨ Key Features

- 💬 **Conversational chat UI** — persistent session history, premium dark glassmorphism design
- 📄 **Source citations** — every answer shows retrieved chunks with similarity scores
- 🎛️ **Adjustable retrieval depth** — top‑K slider to balance context breadth vs. precision
- 🔄 **One‑click re‑ingestion** — rebuild the vector index anytime the document changes
- ✅ **Grounded answers** — responses generated only from indexed document content (reduced hallucination)
- 🧹 **Session controls** — clear conversation, live index status, robust error handling

---

## 🛠️ Tech Stack

| Layer              | Technology                                                       |
|--------------------|------------------------------------------------------------------|
| **Frontend**       | HTML5, CSS3 (glass UI), Vanilla JavaScript                       |
| **Backend API**    | Python 3.10+ (Flask/FastAPI)                                     |
| **PDF parsing**    | pypdf                                                            |
| **Embeddings**     | sentence‑transformers · all‑MiniLM‑L6‑v2 (384‑dim)               |
| **Vector database**| Pinecone (serverless)                                            |
| **LLM**            | Google Gemini API                                                |

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/rag-studio.git
cd rag-studio
2. Install dependencies
bash
pip install -r requirements.txt
3. Set up API keys
Create a .env file in the project root:

env
PINECONE_API_KEY=your_pinecone_key
GOOGLE_API_KEY=your_gemini_key
4. Start the backend server
bash
python app.py          # or uvicorn main:app --reload for FastAPI
```

## 📸 Screenshot
<img width="1429" height="783" alt="Screenshot 2026-09-09 at 3 05 49 PM" src="https://github.com/user-attachments/assets/e57fc219-9b69-4431-8e3d-d1392fff5fbe" />
