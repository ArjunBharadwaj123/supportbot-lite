# routes/upload.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
import pandas as pd
import boto3

from db.session import SessionLocal
from db.models import FAQEntry
from services.embed import get_embeddings


router = APIRouter()

# Create S3 client (uses IAM role automatically on EC2)
s3 = boto3.client("s3")

BUCKET_NAME = "supportbot-documents-1"  # <-- Make sure this matches exactly


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def clear_db(db: Session):
    db.execute(text("TRUNCATE TABLE chat_logs, faq_entries RESTART IDENTITY CASCADE;"))
    db.commit()


@router.post("/faq")
async def upload_faq_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload CSV to S3, generate embeddings, and store FAQs in RDS.
    """

    # --- Validate file type ---
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a valid CSV file.")

    # --- Upload to S3 ---
    try:
        s3.upload_fileobj(
            file.file,
            BUCKET_NAME,
            file.filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {e}")

    # IMPORTANT: Reset file pointer after upload
    file.file.seek(0)

    # --- Clear existing FAQs ---
    clear_db(db)

    # --- Read CSV ---
    try:
        df = pd.read_csv(file.file)
        df.columns = df.columns.str.strip().str.lower()

        rename_map = {}
        if "questions" in df.columns and "question" not in df.columns:
            rename_map["questions"] = "question"
        if "answers" in df.columns and "answer" not in df.columns:
            rename_map["answers"] = "answer"

        if rename_map:
            df.rename(columns=rename_map, inplace=True)

        if not {"question", "answer"}.issubset(df.columns):
            raise HTTPException(status_code=400, detail="Missing required columns: question, answer")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {e}")

    # --- Generate embeddings ---
    questions = df["question"].fillna("").tolist()
    embeddings = get_embeddings(questions)

    # --- Store in DB ---
    for i, row in df.iterrows():
        faq = FAQEntry(
            question=row["question"],
            answer=row["answer"],
            embedding_vector=embeddings[i]
        )
        db.add(faq)

    db.commit()

    return {
        "message": f"Successfully uploaded {len(df)} FAQs.",
        "total": len(df),
        "s3_file": file.filename
    }