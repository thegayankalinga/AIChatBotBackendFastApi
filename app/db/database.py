# app/db/database.py
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.db.models import StaticFact, DynamicFact
from app.db.base import Base

DATABASE_URL = "sqlite:///./knowledge_base.db"  # SQLite database file

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  # SQLite specific
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# def get_db() -> Generator[Session, None, None]:
#     """
#     Dependency-injected session generator.
#     Yields a SQLAlchemy Session for each request.
#     """
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

def initialize_static_facts():
    db = Session(bind=engine)

    static_entries = [
        StaticFact(pattern="hi", response="Hello! How can I assist you today?"),
        StaticFact(pattern="hello", response="Hello there! What can I do for you?"),
        StaticFact(pattern="good morning", response="Good morning! How may I help?"),
        StaticFact(pattern="good afternoon", response="Good afternoon! How can I assist?"),
        StaticFact(pattern="good evening", response="Good evening! What brings you here?"),
        StaticFact(pattern="bye", response="Goodbye! Have a nice day ahead."),
        StaticFact(pattern="thanks", response="You're welcome! Glad I could help."),
        StaticFact(pattern="thank you", response="No problem at all."),
        StaticFact(pattern="what is your name", response="I am your smart assistant."),
        StaticFact(pattern="how are you", response="I am operating at full capacity, thank you!"),
        StaticFact(pattern="what services do you offer", response="I can assist you with banking, accounts, loans, cards, and general information."),
        StaticFact(pattern="types of accounts", response="We offer Current, Savings, and Fixed Deposit Accounts."),
        StaticFact(pattern="types of loans", response="We provide Personal, Home, and Car Loans."),
        StaticFact(pattern="types of credit cards", response="Visa, Mastercard, and Platinum Cards are available."),
        StaticFact(pattern="fixed deposit rates", response="Fixed deposit rates vary between 4% - 6% depending on tenure."),
        StaticFact(pattern="how to apply for a loan", response="You can apply online or visit a branch with necessary documents."),
        StaticFact(pattern="how to open account", response="Opening an account requires valid ID and address proof."),
        StaticFact(pattern="lost my debit card", response="Please immediately block your card through internet banking or call customer service."),
        StaticFact(pattern="reset my online banking password", response="Use the 'Forgot Password' link on the login page to reset your credentials."),
        StaticFact(pattern="tell me a joke", response="Why don't skeletons fight each other? They don't have the guts."),
        StaticFact(pattern="who created you", response="I was created by my talented developers for your assistance."),
        StaticFact(pattern="recommend a saving plan", response="We recommend a combination of a savings account and a fixed deposit for balanced returns."),
        StaticFact(pattern="what is machine learning", response="Machine learning is giving computers the ability to learn without being explicitly programmed."),
        StaticFact(pattern="tell me about deep learning", response="Deep learning is a subset of machine learning based on neural networks with representation learning."),
        StaticFact(pattern="help", response="I am here to help you with banking queries, general questions, and small talk!"),

        # Add these greeting entries at the top
        StaticFact(pattern="greeting", response="Hello! How can I assist you today?"),
        StaticFact(pattern="hi", response="Hi there! What can I do for you?"),
        StaticFact(pattern="hello", response="Hello there! What can I do for you?"),
        StaticFact(pattern="hey", response="Hey! How can I help you out?"),
        StaticFact(pattern="good morning", response="Good morning! How may I help?"),
        StaticFact(pattern="good afternoon", response="Good afternoon! What can I do for you?"),
        StaticFact(pattern="good evening", response="Good evening! What brings you here?"),

        # Your existing entries follow
        StaticFact(pattern="hi", response="Hello! How can I assist you today?"),
        StaticFact(pattern="hello", response="Hello there! What can I do for you?"),
        StaticFact(pattern="good morning", response="Good morning! How may I help?"),
        StaticFact(pattern="good afternoon", response="Good afternoon! How can I assist?"),
        StaticFact(pattern="good evening", response="Good evening! What brings you here?"),
        StaticFact(pattern="bye", response="Goodbye! Have a nice day ahead."),
    ]

    for entry in static_entries:
        existing = db.query(StaticFact).filter_by(pattern=entry.pattern).first()
        if not existing:
            db.add(entry)

    db.commit()
    db.close()

def initialize_dynamic_facts():
    """
    Seed the dynamic_facts table with initial entries if they don't exist.
    """
    db = SessionLocal()
    dynamic_entries = [
        DynamicFact(fact_type="interest_rate_savings", fact_value="3.5% per annum"),
        DynamicFact(fact_type="fixed_deposit_rates",  fact_value="4.0% (6 mo), 4.5% (12 mo), 5.0% (24 mo)"),
        DynamicFact(fact_type="branch_hours",         fact_value="Mon–Fri 9 AM–4 PM; Sat 9 AM–1 PM"),
        DynamicFact(fact_type="loan_processing_time", fact_value="Home loan: 5–7 business days; Personal: 2–3"),
        # If you want the ATM list here, you could store JSON-encoded strings:
        DynamicFact(
            fact_type="atm_locations",
            fact_value='[{"city":"Colombo 03","address":"6/4 Price St."},{"city":"Kandy","address":"52 Temple Rd."}]'
        ),
        DynamicFact(
            fact_type="credit_card_offers",
            fact_value="Visa Platinum: 1.5% cashback; Mastercard Gold: 2% reward points"
        ),
    ]

    for entry in dynamic_entries:
        exists = db.query(DynamicFact).filter_by(fact_type=entry.fact_type).first()
        if not exists:
            db.add(entry)

    db.commit()
    db.close()