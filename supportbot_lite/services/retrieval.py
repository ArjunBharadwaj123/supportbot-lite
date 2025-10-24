# services/retrieval.py
from sqlalchemy import text
from sqlalchemy.orm import Session
from db.models import FAQEntry
from typing import Optional, Tuple

# 1. Search for the most similar FAQ using pgvector, with threshold
def find_best_match(
    db: Session,
    query_embedding,
    top_k: int = 1,
    similarity_threshold: float = 0.4
) -> Optional[Tuple[FAQEntry, float]]:
    """
    Finds the FAQ entry most semantically similar to the given query embedding.
    Returns (FAQEntry, similarity_score) if above threshold, else None.
    """

    # pgvector uses <-> for cosine distance
    sql = text("""
        SELECT id, question, answer, embedding_vector <=> (:query_vector)::vector AS distance
        FROM faq_entries
        ORDER BY distance ASC
        LIMIT :top_k;
    """)

    # Run SQL query (distance search)
    result = db.execute(
        sql, {"query_vector": query_embedding.tolist(), "top_k": top_k}
    ).fetchall()

    if not result:
        return None

    # Take best match
    best = result[0]
    similarity = 1 - best.distance  # convert distance → similarity

    #Distance is between 0 and 2 for cosine, so similarity is between 1 and -1

    # Only return if similarity exceeds threshold
    if similarity < similarity_threshold:
        return None

    faq_entry = FAQEntry(
        id=best.id, question=best.question, answer=best.answer
    )

    return faq_entry, similarity

def get_top_similar_faqs(db: Session, query_embedding, top_k: int = 1):
    """
    Returns the top-k most similar FAQs and their distances.
    Used for debugging and tuning the similarity threshold.
    """
    sql = text("""
        SELECT question, answer, embedding_vector <-> (:query_vector)::vector AS distance
        FROM faq_entries
        ORDER BY distance ASC
        LIMIT :top_k;
    """)

    sql2 = text("""
        SELECT question
        FROM faq_entries
    """)

    rows = db.execute(
        sql, {"query_vector": query_embedding.tolist(), "top_k": top_k}
    ).fetchall()

    rows2 = db.execute(sql2).fetchall()

    print(rows2)

    return [{"question": r.question, "distance": r.distance} for r in rows]