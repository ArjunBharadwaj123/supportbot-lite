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
supportbot-lite/  
├── backend/  
│   ├── app/  
│   │   ├── main.py  
│   │   ├── models.py  
│   │   ├── routes/  
│   │   └── utils/  
│   └── requirements.txt  
├── frontend/  
│   ├── src/  
│   └── package.json  
├── docker-compose.yml  
└── README.md  

---

## ⚙️ Setup & Run Locally

### 1. Clone the repo
\`bash
git clone https://github.com/<your-username>/supportbot-lite.git
cd supportbot-lite
\`

### 2. Start services with Docker
\`bash
docker-compose up --build
\`

The backend will start at `http://localhost:8000`  
The frontend will start at `http://localhost:3000`

---

## 🧠 How It Works
1. CSV FAQ data is uploaded via the FastAPI endpoint.  
2. Each question + answer pair is embedded using SentenceTransformers (MiniLM).  
3. Embeddings are stored in PostgreSQL using **pgvector**.  
4. User queries are embedded and matched by vector similarity.  
5. If similarity falls below a threshold, a fallback LLM generates a paraphrased answer.
