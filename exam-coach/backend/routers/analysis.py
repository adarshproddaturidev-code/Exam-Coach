"""
Router: Weakness Analysis
GET /api/analysis/{student_id}
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, TopicScore, QuestionResult, MockTest
from schemas import AnalysisOut, TopicScoreOut

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])


@router.get("/{student_id}", response_model=AnalysisOut)
def get_analysis(student_id: int, db: Session = Depends(get_db)):
    scores = (
        db.query(TopicScore)
        .filter_by(student_id=student_id)
        .order_by(TopicScore.weakness_score.desc())
        .all()
    )

    # Total question stats
    all_qr = (
        db.query(QuestionResult)
        .join(QuestionResult.mock_test)
        .filter(MockTest.student_id == student_id)
        .all()
    )
    total = len(all_qr)
    correct = sum(1 for q in all_qr if q.is_correct)

    ranked = []
    for i, s in enumerate(scores):
        ranked.append(TopicScoreOut(
            subject=s.subject, topic=s.topic,
            error_rate=s.error_rate, avg_time=s.avg_time,
            mistake_freq=s.mistake_freq, weakness_score=s.weakness_score,
            rank=i + 1,
        ))

    # Split into weak (top 60%) and strong
    mid = max(1, int(len(ranked) * 0.6)) if ranked else 0
    weak = ranked[:mid]
    strong = ranked[mid:]

    return AnalysisOut(
        student_id=student_id,
        total_questions=total,
        total_correct=correct,
        accuracy=round(correct / total * 100, 1) if total else 0,
        weak_topics=weak,
        strong_topics=strong,
    )
