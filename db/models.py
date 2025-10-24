# db/models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from .session import Base

# 1. FAQEntry model: stores each FAQ question, answer, and its embedding
class FAQEntry(Base):
    __tablename__ = "faq_entries"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    embedding_vector = Column(Vector(384))  # 384-dim MiniLM embeddings

    # Relationship to chat logs (one FAQ → many chats)
    chat_logs = relationship("ChatLog", back_populates="matched_faq")


# 2. ChatLog model: stores chat interactions
class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_question = Column(Text, nullable=False)
    matched_question_id = Column(Integer, ForeignKey("faq_entries.id"))
    answer = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Link back to FAQEntry
    matched_faq = relationship("FAQEntry", back_populates="chat_logs")
