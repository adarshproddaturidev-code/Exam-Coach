"""
SQLAlchemy database engine, session factory, and table definitions.
"""
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean,
    DateTime, Text, ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "exam_coach.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ─────────────────────────────────────────────────────────────────────────────
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, default="Student")
    created_at = Column(DateTime, default=datetime.utcnow)

    mock_tests = relationship("MockTest", back_populates="student")
    topic_scores = relationship("TopicScore", back_populates="student")
    study_plans = relationship("StudyPlan", back_populates="student")
    recommendations = relationship("Recommendation", back_populates="student")


class MockTest(Base):
    __tablename__ = "mock_tests"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    raw_json = Column(Text)

    student = relationship("Student", back_populates="mock_tests")
    question_results = relationship("QuestionResult", back_populates="mock_test")


class QuestionResult(Base):
    __tablename__ = "question_results"
    id = Column(Integer, primary_key=True, index=True)
    mock_test_id = Column(Integer, ForeignKey("mock_tests.id"), nullable=False)
    subject = Column(String(100))
    topic = Column(String(200))
    question_id = Column(String(50))
    student_answer = Column(String(10))
    correct_answer = Column(String(10))
    time_taken = Column(Float)          # seconds
    is_correct = Column(Boolean)

    mock_test = relationship("MockTest", back_populates="question_results")


class TopicScore(Base):
    __tablename__ = "topic_scores"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject = Column(String(100))
    topic = Column(String(200))
    error_rate = Column(Float, default=0.0)
    avg_time = Column(Float, default=0.0)
    mistake_freq = Column(Integer, default=0)
    weakness_score = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="topic_scores")


class StudyPlan(Base):
    __tablename__ = "study_plans"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    plan_json = Column(Text)

    student = relationship("Student", back_populates="study_plans")


class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    recs_json = Column(Text)

    student = relationship("Student", back_populates="recommendations")


# ─────────────────────────────────────────────────────────────────────────────
def init_db():
    """Create all tables and seed a default student if needed."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(Student).filter_by(id=1).first():
            db.add(Student(id=1, name="Demo Student"))
            db.commit()
    finally:
        db.close()


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
