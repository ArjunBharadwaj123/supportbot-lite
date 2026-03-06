# routes/upload.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
import pandas as pd
import boto3
import uuid
import io

from db.session import SessionLocal
from db.models import FAQEntry, UploadedFile
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
    Upload CSV to S3, generate embeddings, store metadata + FAQs in RDS.
    """

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a valid CSV file.")

    # Read file into memory once
    contents = await file.read()

    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Generate unique S3 key
    unique_key = f"{uuid.uuid4()}-{file.filename}"

    # Upload to S3
    try:
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=unique_key,
            Body=contents
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {e}")

    # Store metadata in DB
    from db.models import UploadedFile

    uploaded_file = UploadedFile(
        filename=file.filename,
        s3_key=unique_key,
        file_size=len(contents)
    )

    db.add(uploaded_file)
    db.commit()

    # Read CSV from memory
    try:
        df = pd.read_csv(io.BytesIO(contents))
        df.columns = df.columns.str.strip().str.lower()

        if not {"question", "answer"}.issubset(df.columns):
            raise HTTPException(status_code=400, detail="Missing required columns: question, answer")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {e}")

    # Clear old FAQs
    clear_db(db)

    # Generate embeddings
    questions = df["question"].fillna("").tolist()
    embeddings = get_embeddings(questions)

    # Store FAQs
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
        "s3_key": unique_key
    }