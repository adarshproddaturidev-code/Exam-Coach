"""
Router: Study Material Recommendations
POST /api/recommendations/{student_id}
GET  /api/recommendations/{student_id}/latest
"""
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, TopicScore, Recommendation
from schemas import RecommendationOut
from services.llm_client import generate_recommendations
from datetime import datetime

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.post("/{student_id}", response_model=RecommendationOut)
def create_recommendations(student_id: int, db: Session = Depends(get_db)):
    scores = (
        db.query(TopicScore)
        .filter_by(student_id=student_id)
        .order_by(TopicScore.weakness_score.desc())
        .limit(6)
        .all()
    )
    weak = [
        {
            "subject": s.subject, "topic": s.topic,
            "weakness_score": s.weakness_score,
            "error_rate": s.error_rate, "avg_time": s.avg_time,
            "mistake_freq": s.mistake_freq,
        }
        for s in scores
    ]
    recs = generate_recommendations(weak)

    rec = Recommendation(student_id=student_id, recs_json=json.dumps(recs))
    db.add(rec)
    db.commit()
    db.refresh(rec)

    return RecommendationOut(student_id=student_id, created_at=rec.created_at, recommendations=recs)


@router.get("/{student_id}/latest", response_model=RecommendationOut)
def get_latest_recommendations(student_id: int, db: Session = Depends(get_db)):
    rec = (
        db.query(Recommendation)
        .filter_by(student_id=student_id)
        .order_by(Recommendation.created_at.desc())
        .first()
    )
    if not rec:
        return RecommendationOut(student_id=student_id, created_at=datetime.utcnow(), recommendations={"recommendations": []})
    return RecommendationOut(student_id=student_id, created_at=rec.created_at, recommendations=json.loads(rec.recs_json))
