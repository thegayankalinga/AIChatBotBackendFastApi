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

@router.post("/techme")
async def teach_bot(request: TeachRequest):
    db = SessionLocal()
    try:
        # Check if the question already exists
        existing = db.query(LearnedResponse).filter_by(question=request.question.lower()).first()
        if existing:
            return error_response("This question has already been taught.")

        new_fact = LearnedResponse(
            question=request.question.lower(),
            answer=request.answer
        )
        db.add(new_fact)
        db.commit()
        return success_response("Thank you for teaching me!", {"question": request.question})
    except Exception as e:
        db.rollback()
        return error_response(f"An error occurred: {str(e)}")
    finally:
        db.close()