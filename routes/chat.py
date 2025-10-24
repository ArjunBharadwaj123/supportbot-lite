# routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.embed import get_embedding
from services.retrieval import get_top_similar_faqs
from db.session import SessionLocal
from db.models import ChatLog
from services.embed import get_embedding
from services.retrieval import find_best_match
import requests
import os

router = APIRouter()

# 1️⃣ Dependency to get a DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2️⃣ Chat endpoint: process user questions
@router.post("/")
async def chat_with_bot(payload: dict, db: Session = Depends(get_db)):
    """
    Receives a user question, searches for the best FAQ match,
    and replies with either a stored answer or a LLaMA3-generated response.
    """

    # --- Step 1: Extract user question ---
    user_question = payload.get("question")
    if not user_question:
        raise HTTPException(status_code=400, detail="Missing 'question' field in request body.")

    # --- Step 2: Embed user question ---
    user_embedding = get_embedding(user_question)

    # --- Step 3: Search for the closest FAQ ---
    match = find_best_match(db, user_embedding, similarity_threshold=0.75)

    # --- Step 4: Determine answer source ---
    if match:
        faq_entry, similarity = match
        answer = faq_entry.answer
        source = "faq"
    else:
        # Low similarity → call LLaMA3 for fallback answer
        answer = generate_llama3_response(user_question)
        similarity = 0.0
        source = "llm"

    # --- Step 5: Log chat interaction ---
    chat_log = ChatLog(
        user_question=user_question,
        matched_question_id=faq_entry.id if match else None,
        answer=answer
    )
    db.add(chat_log)
    db.commit()

    # --- Step 6: Return structured response ---
    return {
        "question": user_question,
        "answer": answer,
        "similarity": round(similarity, 3),
        "source": source
    }


# 3️⃣ Helper: call LLaMA3 locally via Ollama API
def generate_llama3_response(prompt: str) -> str:
    """
    Calls the LLaMA3 model locally using Ollama.
    Make sure 'ollama serve' is running with a model pulled (e.g., 'ollama pull llama3').
    """
    try:
        response = requests.post(
            os.getenv("LLAMA3_URL"),
            json={
                "model": os.getenv("LLAMA3_MODEL", "llama3"),
                "prompt": prompt,
                "stream": False,       # ✅ one JSON response instead of many
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "I'm not sure how to answer that.")
    except Exception as e:
        return f"⚠️ LLaMA3 unavailable: {e}"


@router.post("/debug")
async def debug_query(request: dict, db: Session = Depends(get_db)):
    prompt = request.get("question", "")
    query_vector = get_embedding(prompt)
    results = get_top_similar_faqs(db, query_vector, top_k=5)
    return results