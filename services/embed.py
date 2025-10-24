# services/embed.py
from sentence_transformers import SentenceTransformer
import numpy as np

# 1. Load the MiniLM model once at startup
model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Generate embedding for a single text
def get_embedding(text: str) -> np.ndarray:
    """
    Converts input text into a dense vector representation.
    """
    if not text or not text.strip():
        return np.zeros(384)  # fallback for empty strings
    embedding = model.encode(text, normalize_embeddings=True)
    return np.array(embedding, dtype=np.float32)

# 3. Generate embeddings for a list of texts
def get_embeddings(texts: list[str]) -> list[np.ndarray]:
    """
    Converts multiple strings into their embeddings in one batch.
    """
    if not texts:
        return []
    embeddings = model.encode(texts, normalize_embeddings=True)
    return [np.array(vec, dtype=np.float32) for vec in embeddings]
