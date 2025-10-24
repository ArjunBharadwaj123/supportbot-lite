# routes/__init__.py
from fastapi import APIRouter
from .upload import router as upload_router
from .chat import router as chat_router

router = APIRouter()
router.include_router(upload_router, prefix="/upload", tags=["Upload"])
router.include_router(chat_router, prefix="/chat", tags=["Chat"])
