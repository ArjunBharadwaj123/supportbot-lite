# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import upload, chat
from db.session import init_db
from routes import router as api_router

# 1. Create the FastAPI app instance
app = FastAPI(
    title="SupportBot Lite",
    description="An FAQ chatbot that answers using CSV uploads and pgvector search.",
    version="1.0.0",
)

# Include the main API router
app.include_router(api_router)

# 2. Allow CORS so frontend (React) can call the backend API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, replace "*" with your React URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Include route files
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

# 4. Initialize the database on startup
@app.on_event("startup")
async def on_startup():
    init_db()

# 5. Root endpoint (for quick health check)
@app.get("/")
def root():
    return {"message": "SupportBot Lite API is running 🚀"}
