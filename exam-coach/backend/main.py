"""
FastAPI Application Entry Point
"""
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import init_db
from routers import tests, analysis, study_plan, recommendations, progress, auth

app = FastAPI(
    title="Personalized Entrance Exam Coach API",
    description="AI-powered mock test analyser, weak topic identifier, and study plan generator.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(tests.router)
app.include_router(analysis.router)
app.include_router(study_plan.router)
app.include_router(recommendations.router)
app.include_router(progress.router)
app.include_router(auth.router)

# Serve frontend static files
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
SAMPLE_DATA_DIR = Path(__file__).parent.parent / "sample_data"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

if SAMPLE_DATA_DIR.exists():
    app.mount("/sample_data", StaticFiles(directory=str(SAMPLE_DATA_DIR)), name="sample_data")

    @app.get("/", response_class=FileResponse)
    def serve_frontend():
        return str(FRONTEND_DIR / "index.html")

    @app.get("/login", response_class=FileResponse)
    def serve_login():
        return str(FRONTEND_DIR / "login.html")


@app.on_event("startup")
def startup_event():
    init_db()
    print("[OK] Database initialised")
    print("[OK] Exam Coach API running at http://localhost:8000")
    print("[OK] API docs at http://localhost:8000/docs")


@app.get("/health")
def health():
    return {"status": "ok", "message": "Exam Coach API is healthy"}
