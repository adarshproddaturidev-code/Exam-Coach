"""
Weakness Scoring Service
Formula: Weakness Score = (Error Rate × 0.6) + (Norm Avg Time × 0.2) + (Mistake Freq × 0.2)
"""
from sqlalchemy.orm import Session
from database import QuestionResult, TopicScore
from datetime import datetime
from collections import defaultdict


def compute_and_store_scores(db: Session, student_id: int, mock_test_id: int):
    """
    Reads all QuestionResults for this student, computes per-topic weakness scores,
    and upserts them into TopicScore.
    """
    # Fetch ALL results for the student (across all tests for cumulative accuracy)
    all_results = (
        db.query(QuestionResult)
        .join(QuestionResult.mock_test)
        .filter_by(student_id=student_id)
        .all()
    )

    # Aggregate per topic
    topic_data = defaultdict(lambda: {"subject": "", "correct": 0, "total": 0, "times": [], "wrongs": 0})

    for r in all_results:
        key = (r.subject, r.topic)
        topic_data[key]["subject"] = r.subject
        topic_data[key]["total"] += 1
        if r.is_correct:
            topic_data[key]["correct"] += 1
        else:
            topic_data[key]["wrongs"] += 1
        topic_data[key]["times"].append(r.time_taken)

    if not topic_data:
        return

    # Compute raw metrics
    raw_scores = []
    all_times = [t for d in topic_data.values() for t in d["times"]]
    max_time = max(all_times) if all_times else 1
    max_mistakes = max(d["wrongs"] for d in topic_data.values()) or 1

    for (subject, topic), d in topic_data.items():
        error_rate = 1 - (d["correct"] / d["total"]) if d["total"] else 0
        avg_time = sum(d["times"]) / len(d["times"]) if d["times"] else 0
        mistake_freq = d["wrongs"]

        # Normalise avg_time and mistake_freq to [0, 1]
        norm_time = avg_time / max_time
        norm_mistakes = mistake_freq / max_mistakes

        weakness_score = (error_rate * 0.6) + (norm_time * 0.2) + (norm_mistakes * 0.2)

        raw_scores.append({
            "subject": subject,
            "topic": topic,
            "error_rate": round(error_rate, 4),
            "avg_time": round(avg_time, 2),
            "mistake_freq": mistake_freq,
            "weakness_score": round(weakness_score, 4),
        })

    # Upsert into DB
    for s in raw_scores:
        existing = (
            db.query(TopicScore)
            .filter_by(student_id=student_id, subject=s["subject"], topic=s["topic"])
            .first()
        )
        if existing:
            existing.error_rate = s["error_rate"]
            existing.avg_time = s["avg_time"]
            existing.mistake_freq = s["mistake_freq"]
            existing.weakness_score = s["weakness_score"]
            existing.updated_at = datetime.utcnow()
        else:
            db.add(TopicScore(student_id=student_id, **s))

    db.commit()
