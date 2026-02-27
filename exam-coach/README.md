# Personalized Entrance Exam Coach

An **AI-powered entrance exam preparation** platform — built with FastAPI, SQLite, and a dark-mode SPA frontend.

## 🚀 Quick Start

```powershell
cd C:\Users\HP\Desktop\Test4\exam-coach
powershell -ExecutionPolicy Bypass -File start.ps1
```

Then open **http://localhost:8000** in your browser.

---

## 📁 Project Structure

```
exam-coach/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── database.py              # SQLAlchemy models + DB init
│   ├── schemas.py               # Pydantic request/response schemas
│   ├── requirements.txt
│   ├── .env.example             # Copy to .env and add API key
│   ├── routers/
│   │   ├── tests.py             # POST /api/tests/submit
│   │   ├── analysis.py          # GET  /api/analysis/{id}
│   │   ├── study_plan.py        # POST/GET /api/study-plan/{id}
│   │   ├── recommendations.py   # POST/GET /api/recommendations/{id}
│   │   └── progress.py          # GET  /api/progress/{id}
│   └── services/
│       ├── weakness_scorer.py   # Scoring algorithm
│       └── llm_client.py        # OpenAI wrapper + template fallback
├── frontend/
│   ├── index.html               # Single-page app
│   ├── style.css                # Dark glassmorphism theme
│   └── app.js                   # All interactivity + charts
├── sample_data/
│   └── mock_test_sample.json    # 30-question demo dataset
└── start.ps1                    # One-click launcher
```

## 🔑 LLM API Configuration

Edit `backend/.env`:
```
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

> **Without an API key**: The app falls back to template-based study plans and recommendations — all other features work perfectly.

## 🧮 Weakness Score Formula

```
Weakness Score = (Error Rate × 0.6) + (Norm Avg Time × 0.2) + (Norm Mistake Freq × 0.2)
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/tests/submit` | Submit mock test JSON |
| `GET`  | `/api/analysis/{student_id}` | Ranked weak/strong topics |
| `POST` | `/api/study-plan/{student_id}` | Generate 7-day AI study plan |
| `GET`  | `/api/study-plan/{student_id}/latest` | Get latest study plan |
| `POST` | `/api/recommendations/{student_id}` | Generate material recommendations |
| `GET`  | `/api/recommendations/{student_id}/latest` | Get latest recommendations |
| `GET`  | `/api/progress/{student_id}` | Progress history for charts |
| `GET`  | `/docs` | Interactive Swagger API docs |
