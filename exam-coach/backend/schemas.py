"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime


# ── Incoming ─────────────────────────────────────────────────────────────────
class QuestionIn(BaseModel):
    subject: str
    topic: str
    question_id: str
    student_answer: str
    correct_answer: str
    time_taken: float = Field(..., description="Seconds taken to answer")


class MockTestIn(BaseModel):
    student_id: int = 1
    questions: List[QuestionIn]


# ── Outgoing ──────────────────────────────────────────────────────────────────
class TopicScoreOut(BaseModel):
    subject: str
    topic: str
    error_rate: float
    avg_time: float
    mistake_freq: int
    weakness_score: float
    rank: int

    class Config:
        from_attributes = True


class AnalysisOut(BaseModel):
    student_id: int
    total_questions: int
    total_correct: int
    accuracy: float
    weak_topics: List[TopicScoreOut]
    strong_topics: List[TopicScoreOut]


class StudyPlanOut(BaseModel):
    student_id: int
    created_at: datetime
    plan: Any          # parsed JSON from LLM


class RecommendationOut(BaseModel):
    student_id: int
    created_at: datetime
    recommendations: Any  # parsed JSON from LLM


class ProgressPoint(BaseModel):
    test_number: int
    submitted_at: datetime
    accuracy: float
    avg_time: float
    total_questions: int


class ProgressOut(BaseModel):
    student_id: int
    history: List[ProgressPoint]
    topic_scores: List[TopicScoreOut]
