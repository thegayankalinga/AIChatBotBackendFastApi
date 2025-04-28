# app/routes/admin.py

from fastapi import APIRouter
from app.db.database import SessionLocal
from app.db.models import DynamicFact, StaticFact, LearnedResponse
from app.utils.response_format import success_response, error_response

router = APIRouter()

@router.get("/admin/show_dynamic_facts")
async def show_dynamic_facts():
    db = SessionLocal()
    try:
        facts = db.query(DynamicFact).all()
        facts_data = [{"fact_type": fact.fact_type, "fact_value": fact.fact_value} for fact in facts]
        return success_response("Dynamic facts retrieved successfully", {"dynamic_facts": facts_data})
    except Exception as e:
        return error_response(f"An error occurred: {str(e)}")
    finally:
        db.close()


@router.post("/admin/delete_all_records")
async def delete_all_records():
    db = SessionLocal()
    try:
        db.query(StaticFact).delete()
        db.query(DynamicFact).delete()
        db.query(LearnedResponse).delete()
        db.commit()
        return success_response("All records deleted successfully.")
    except Exception as e:
        db.rollback()
        return error_response(f"An error occurred: {str(e)}")
    finally:
        db.close()