# app/db/models.py

from sqlalchemy import Column, String, Integer
from app.db.base import Base

class StaticFact(Base):
    __tablename__ = "static_facts"

    pattern = Column(String, primary_key=True, index=True)
    response = Column(String)

class DynamicFact(Base):
    __tablename__ = "dynamic_facts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fact_type = Column(String, index=True)
    fact_value = Column(String)

class LearnedResponse(Base):
    __tablename__ = "learned_responses"

    question = Column(String, primary_key=True, index=True)
    answer = Column(String)


