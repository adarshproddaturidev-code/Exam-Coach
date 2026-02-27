"""
Router: Student Progress
GET /api/progress/{student_id}
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db, MockTest, QuestionResult, TopicScore
from schemas import ProgressOut, ProgressPoint, TopicScoreOut

router = APIRouter(prefix="/api/progress", tags=["Progress"])


@router.get("/{student_id}", response_model=ProgressOut)
def get_progress(student_id: int, db: Session = Depends(get_db)):
    tests = (
        db.query(MockTest)
        .filter_by(student_id=student_id)
        .order_by(MockTest.submitted_at.asc())
        .all()
    )

    history = []
    for i, test in enumerate(tests):
        qrs = test.question_results
        total = len(qrs)
        correct = sum(1 for q in qrs if q.is_correct)
        times = [q.time_taken for q in qrs]
        avg_time = round(sum(times) / len(times), 1) if times else 0
        accuracy = round(correct / total * 100, 1) if total else 0
        history.append(ProgressPoint(
            test_number=i + 1,
            submitted_at=test.submitted_at,
            accuracy=accuracy,
            avg_time=avg_time,
            total_questions=total,
        ))

    scores = (
        db.query(TopicScore)
        .filter_by(student_id=student_id)
        .order_by(TopicScore.weakness_score.desc())
        .all()
    )
    topic_scores = [
        TopicScoreOut(
            subject=s.subject, topic=s.topic,
            error_rate=s.error_rate, avg_time=s.avg_time,
            mistake_freq=s.mistake_freq, weakness_score=s.weakness_score,
            rank=i + 1,
        )
        for i, s in enumerate(scores)
    ]

    return ProgressOut(student_id=student_id, history=history, topic_scores=topic_scores)
