# app/routes/techme.py

from fastapi import APIRouter
from pydantic import BaseModel
from app.db.database import SessionLocal
from app.db.models import LearnedResponse
from app.utils.response_format import success_response, error_response

router = APIRouter()

class TeachRequest(BaseModel):
    question: str
    answer: str


@router.get("/", summary="List all user-taught Q&A")
async def list_taught():
    db = SessionLocal()
    all_ = db.query(LearnedResponse).all()
    db.close()
    return success_response("All learned responses", {
        "items": [{"question": x.question, "answer": x.answer} for x in all_]
    })

@router.post("/", summary="Teach the bot a new question/answer pair")
async def teach_bot(request: TeachRequest):
    db = SessionLocal()
    q = request.question.strip().lower()
    a = request.answer.strip()
    try:
        # Check if the question already exists
        existing = db.query(LearnedResponse).filter_by(question=q).first()
        if existing:
            return error_response("This question has already been taught.")

        new_fact = LearnedResponse(
            question=q,
            answer=a
        )
        db.add(new_fact)
        db.commit()
        return success_response("Thank you for teaching me!", {"question": request.question})
    except Exception as e:
        db.rollback()
        return error_response(f"An error occurred: {str(e)}")
    finally:
        db.close()

