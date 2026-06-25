# SupportBot Lite

A retrieval-augmented chatbot that ingests FAQ data from a CSV, encodes it into semantic embeddings using SentenceTransformers, stores them in PostgreSQL via pgvector, and answers user questions by finding the closest matching FAQ. When no strong match is found, it falls back to LLaMA 3 (via Ollama) for a generated response.

Built with FastAPI (backend) and React (frontend), fully containerized with Docker Compose.

---

## How It Works

1. Upload a CSV of FAQs through the UI or API.
2. Each question is embedded using `all-MiniLM-L6-v2` and stored in PostgreSQL with pgvector.
3. On a user query, the question is embedded and compared against stored vectors using cosine similarity.
4. If similarity exceeds the configured threshold (default `0.75`), the matched FAQ answer is returned.
5. Otherwise, the query is forwarded to LLaMA 3 running locally via Ollama for a generated answer.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Uvicorn |
| Embeddings | SentenceTransformers (`all-MiniLM-L6-v2`) |
| Vector Store | PostgreSQL + pgvector |
| ORM / Migrations | SQLAlchemy, Alembic |
| LLM Fallback | LLaMA 3 via Ollama |
| Frontend | React |
| Containerization | Docker, Docker Compose |
| Cloud (optional) | AWS (boto3) |

---

## Project Structure

```
supportbot-lite/
├── api/          # FastAPI app (main.py, models, etc.)
├── db/           # Database setup and migrations
├── routes/       # API route definitions
├── services/     # Embedding and LLM logic
├── uploads/      # Uploaded FAQ CSVs
├── web/          # React frontend
├── .env          # Environment variables (see below)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Prerequisites

- [Docker & Docker Compose](https://docs.docker.com/get-docker/)
- [Ollama](https://ollama.com/) running locally with LLaMA 3 pulled:
  ```bash
  ollama pull llama3
  ollama serve
  ```

---

## Setup & Running

### 1. Clone the repository

```bash
git clone https://github.com/ArjunBharadwaj123/supportbot-lite.git
cd supportbot-lite
```

### 2. Configure environment variables

The `.env` file at the root is pre-configured with defaults:

```env
EMBEDDING_MODEL=all-MiniLM-L6-v2

LLAMA3_URL=http://host.docker.internal:11434/api/generate
LLAMA3_MODEL=llama3

SIMILARITY_THRESHOLD=0.75
ENV=development
```

Update `LLAMA3_URL` if your Ollama instance is running somewhere other than localhost. You'll also need to add your PostgreSQL connection string — for example:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/supportbot
```

### 3. Start the services

```bash
docker compose up --build
```

This spins up:
- The **FastAPI backend** at `http://localhost:8000`
- The **React frontend** at `http://localhost:3000`

---

## Usage

1. Open `http://localhost:3000` in your browser.
2. Upload a CSV file with at least two columns: a question column and an answer column.
3. The backend will embed each FAQ and store it in pgvector.
4. Type a question in the chat interface — the bot will return the closest matching FAQ answer, or fall back to LLaMA 3 if no strong match is found.

You can also interact directly with the API at `http://localhost:8000/docs` (Swagger UI).

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | SentenceTransformers model for encoding |
| `LLAMA3_URL` | `http://host.docker.internal:11434/api/generate` | Ollama API endpoint |
| `LLAMA3_MODEL` | `llama3` | LLM model name |
| `SIMILARITY_THRESHOLD` | `0.75` | Minimum cosine similarity to return a FAQ match |
| `ENV` | `development` | App environment |

---

## Dependencies

Install manually (if running outside Docker):

```bash
pip install -r requirements.txt
```

Key packages: `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg2-binary`, `pgvector`, `sentence-transformers`, `torch`, `pandas`, `alembic`, `python-dotenv`, `boto3`

---

## Notes

- The `.env` file is committed to this repo for convenience but should be gitignored in any production deployment.
- The `supportbot-key-2.pem` file in the root is an EC2 key pair used for deployment and should never be shared publicly.
- Ollama must be running on the host machine before starting Docker Compose — the backend reaches it via `host.docker.internal`.

---

## Author

**Arjun Bharadwaj** — [github.com/ArjunBharadwaj123](https://github.com/ArjunBharadwaj123)
