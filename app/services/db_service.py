# app/services/db_service.py

from sqlalchemy.orm import Session
from app.db.models import StaticFact, LearnedResponse
from app.db.database import SessionLocal

def get_static_response(pattern: str):
    db: Session = SessionLocal()
    fact = db.query(StaticFact).filter(StaticFact.pattern == pattern).first()
    db.close()
    return fact.response if fact else None

def get_learned_response(question: str):
    db: Session = SessionLocal()
    fact = db.query(LearnedResponse).filter(LearnedResponse.question == question).first()
    db.close()
    return fact.answer if fact else None