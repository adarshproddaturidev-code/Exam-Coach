"""
Router: 7-Day Study Plan
POST /api/study-plan/{student_id}
GET  /api/study-plan/{student_id}/latest
"""
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, TopicScore, StudyPlan
from schemas import StudyPlanOut
from services.llm_client import generate_study_plan
from datetime import datetime

router = APIRouter(prefix="/api/study-plan", tags=["Study Plan"])


def _get_weak_topics(db: Session, student_id: int) -> list[dict]:
    scores = (
        db.query(TopicScore)
        .filter_by(student_id=student_id)
        .order_by(TopicScore.weakness_score.desc())
        .all()
    )
    return [
        {
            "subject": s.subject, "topic": s.topic,
            "weakness_score": s.weakness_score,
            "error_rate": s.error_rate, "avg_time": s.avg_time,
        }
        for s in scores
    ]


@router.post("/{student_id}", response_model=StudyPlanOut)
def create_study_plan(student_id: int, db: Session = Depends(get_db)):
    weak = _get_weak_topics(db, student_id)
    plan = generate_study_plan(weak)

    sp = StudyPlan(student_id=student_id, plan_json=json.dumps(plan))
    db.add(sp)
    db.commit()
    db.refresh(sp)

    return StudyPlanOut(student_id=student_id, created_at=sp.created_at, plan=plan)


@router.get("/{student_id}/latest", response_model=StudyPlanOut)
def get_latest_plan(student_id: int, db: Session = Depends(get_db)):
    sp = (
        db.query(StudyPlan)
        .filter_by(student_id=student_id)
        .order_by(StudyPlan.created_at.desc())
        .first()
    )
    if not sp:
        return StudyPlanOut(student_id=student_id, created_at=datetime.utcnow(), plan={"days": []})
    return StudyPlanOut(student_id=student_id, created_at=sp.created_at, plan=json.loads(sp.plan_json))
