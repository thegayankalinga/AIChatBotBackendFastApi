from sqlalchemy.orm import Session
from app.db.models import StaticFact, LearnedResponse, DynamicFact
from app.db.database import SessionLocal


def get_static_response(pattern: str) -> str | None:
    db: Session = SessionLocal()
    fact = db.query(StaticFact).filter(StaticFact.pattern == pattern).first()
    db.close()
    return fact.response if fact else None


def get_learned_response(question: str) -> str | None:
    db: Session = SessionLocal()
    fact = db.query(LearnedResponse).filter(LearnedResponse.question == question).first()
    db.close()
    return fact.answer if fact else None


def get_dynamic_fact(fact_type: str) -> str | None:
    """Retrieve a dynamic fact by its type."""
    db: Session = SessionLocal()
    fact = db.query(DynamicFact).filter(DynamicFact.fact_type == fact_type).first()
    db.close()
    return fact.fact_value if fact else None


def set_dynamic_fact(fact_type: str, fact_value: str) -> None:
    """Create or update a dynamic fact."""
    db: Session = SessionLocal()
    existing = db.query(DynamicFact).filter(DynamicFact.fact_type == fact_type).first()
    if existing:
        existing.fact_value = fact_value
    else:
        db.add(DynamicFact(fact_type=fact_type, fact_value=fact_value))
    db.commit()
    db.close()


def delete_dynamic_fact(fact_type: str) -> bool:
    """Delete a dynamic fact; returns True if deleted."""
    db: Session = SessionLocal()
    rows = db.query(DynamicFact).filter(DynamicFact.fact_type == fact_type).delete()
    db.commit()
    db.close()
    return bool(rows)

def delete_all_dynamic_facts() -> int:
    """
    Remove all entries from the dynamic_facts table.
    Returns the number of rows deleted.
    """
    db: Session = SessionLocal()
    deleted_count = db.query(DynamicFact).delete()
    db.commit()
    db.close()
    return deleted_count

def delete_learned_response(question: str) -> bool:
    """
    Delete a user-taught Q&A by its question (intent tag).
    Returns True if a row was deleted.
    """
    db: Session = SessionLocal()
    count = db.query(LearnedResponse).filter(LearnedResponse.question == question).delete()
    db.commit()
    db.close()
    return bool(count)


def set_static_fact(pattern: str, response: str) -> None:
    """
    Create or update a static fact (pattern→response).
    """
    db: Session = SessionLocal()
    existing = db.query(StaticFact).filter(StaticFact.pattern == pattern).first()
    if existing:
        existing.response = response
    else:
        db.add(StaticFact(pattern=pattern, response=response))
    db.commit()
    db.close()


def delete_static_fact(pattern: str) -> bool:
    """
    Delete a static fact by its pattern.
    Returns True if a row was deleted.
    """
    db: Session = SessionLocal()
    count = db.query(StaticFact).filter(StaticFact.pattern == pattern).delete()
    db.commit()
    db.close()
    return bool(count)


def get_all_static_facts() -> list[dict]:
    """
    List all static facts.
    """
    db: Session = SessionLocal()
    facts = db.query(StaticFact).all()
    db.close()
    return [{"pattern": f.pattern, "response": f.response} for f in facts]
