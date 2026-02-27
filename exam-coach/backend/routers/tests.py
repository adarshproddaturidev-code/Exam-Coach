"""
Router: Mock Test Submission
POST /api/tests/submit
"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, MockTest, QuestionResult
from schemas import MockTestIn
from services.weakness_scorer import compute_and_store_scores

router = APIRouter(prefix="/api/tests", tags=["Tests"])


@router.post("/submit")
def submit_test(payload: MockTestIn, db: Session = Depends(get_db)):
    # Persist mock test record
    mt = MockTest(student_id=payload.student_id, raw_json=json.dumps(payload.model_dump()))
    db.add(mt)
    db.flush()  # get mt.id

    # Persist each question result
    for q in payload.questions:
        is_correct = q.student_answer.strip().upper() == q.correct_answer.strip().upper()
        db.add(QuestionResult(
            mock_test_id=mt.id,
            subject=q.subject,
            topic=q.topic,
            question_id=q.question_id,
            student_answer=q.student_answer,
            correct_answer=q.correct_answer,
            time_taken=q.time_taken,
            is_correct=is_correct,
        ))
    db.commit()

    # Recompute weakness scores
    compute_and_store_scores(db, payload.student_id, mt.id)

    total = len(payload.questions)
    correct = sum(
        1 for q in payload.questions
        if q.student_answer.strip().upper() == q.correct_answer.strip().upper()
    )
    return {
        "message": "Test submitted and analysed successfully.",
        "mock_test_id": mt.id,
        "total_questions": total,
        "correct": correct,
        "accuracy": round(correct / total * 100, 1) if total else 0,
    }
