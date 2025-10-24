# routes/upload.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
import pandas as pd
from db.session import SessionLocal
from db.models import FAQEntry
from services.embed import get_embeddings

router = APIRouter()

# 1️⃣ Dependency to get a new DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def clear_db(db: Session):
    """Utility function to clear all FAQ entries from the database."""
    db.execute(text("TRUNCATE TABLE chat_logs, faq_entries RESTART IDENTITY CASCADE;"))
    db.commit()

# 2️⃣ Upload and process a CSV file of FAQs
@router.post("/faq")
async def upload_faq_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Accepts a CSV file with 'question' and 'answer' columns,
    embeds the questions, and stores them in the database.
    """
    # --- Step 1: Validate file type ---
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a valid CSV file.")

    clear_db(db)  # Clear existing FAQs

    # --- Step 2: Read CSV into DataFrame ---
    try:
        # Read CSV and normalize column names
        df = pd.read_csv(file.file)
        df.columns = df.columns.str.strip().str.lower()

        # ✅ Accept both singular/plural variants
        rename_map = {}
        if "questions" in df.columns and "question" not in df.columns:
            rename_map["questions"] = "question"
        if "answers" in df.columns and "answer" not in df.columns:
            rename_map["answers"] = "answer"

        if rename_map:
            df.rename(columns=rename_map, inplace=True)

        # ✅ Validate columns after renaming
        if not {"question", "answer"}.issubset(df.columns):
            raise HTTPException(status_code=400, detail="Missing required columns: question, answer")
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {e}")

    # --- Step 3: Validate required columns ---
    if "question" not in df.columns or "answer" not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must contain 'question' and 'answer' columns.")

    # --- Step 4: Generate embeddings for questions ---
    questions = df["question"].fillna("").tolist()
    embeddings = get_embeddings(questions)

    # --- Step 5: Store entries in database ---
    for i, row in df.iterrows():
        faq = FAQEntry(
            question=row["question"],
            answer=row["answer"],
            embedding_vector=embeddings[i]
        )
        db.add(faq)

    db.commit()

    # --- Step 6: Return summary ---
    return {
        "message": f"✅ Successfully uploaded {len(df)} FAQs.",
        "total": len(df)
    }
