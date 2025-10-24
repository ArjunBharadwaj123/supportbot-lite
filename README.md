# SupportBot Lite 🤖

SupportBot Lite is a retrieval-augmented chatbot that transforms CSV-based FAQ data into searchable embeddings for natural-language question answering. It uses **SentenceTransformers** for embedding generation, **pgvector** in PostgreSQL for vector similarity search, and a **FastAPI** backend with a **React** frontend for an interactive chat experience.

---

## 🚀 Features
- Upload a CSV of FAQs and automatically generate vector embeddings.
- Perform **semantic search** for paraphrased user queries.
- Use **LLM-based fallback** for unrecognized questions.
- REST API built with **FastAPI** for CSV upload and retrieval.
- Responsive **React frontend** for real-time chat.
- Fully containerized with **Docker Compose** for reproducible deployment.

---

## 🧩 Tech Stack
**Backend:** FastAPI, SentenceTransformers (MiniLM), PostgreSQL + pgvector  
**Frontend:** React, Axios  
**Containerization:** Docker Compose  

---

## 📂 Project Structure
