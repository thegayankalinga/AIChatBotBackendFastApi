# app/routes/admin.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any
from app.services.db_service import (
    get_dynamic_fact,
    set_dynamic_fact,
    delete_dynamic_fact, delete_all_dynamic_facts,
    delete_learned_response,
    set_static_fact,
    delete_static_fact,
    get_all_static_facts,
)
from app.utils.response_format import success_response, error_response

router = APIRouter(
    tags=["Admin"]
)

class DynamicFactIn(BaseModel):
    fact_type: str
    fact_value: str

class DynamicFactOut(DynamicFactIn):
    pass

@router.get("/dynamic-facts")
async def list_dynamic_facts():
    # This should return all fact_type and values. For simplicity:
    from app.db.database import SessionLocal
    from app.db.models import DynamicFact
    db = SessionLocal()
    facts = db.query(DynamicFact).all()
    db.close()
    return success_response("Listed dynamic facts", {
        "items": [ {"fact_type": f.fact_type, "fact_value": f.fact_value} for f in facts ]
    })

@router.post("/dynamic-facts")
async def create_or_update_dynamic(f: DynamicFactIn):
    try:
        set_dynamic_fact(f.fact_type, f.fact_value)
        return success_response("Dynamic fact saved", {"fact_type": f.fact_type})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/dynamic-facts/{fact_type}")
async def remove_dynamic(fact_type: str):
    deleted = delete_dynamic_fact(fact_type)
    if not deleted:
        raise HTTPException(status_code=404, detail="Fact not found")
    return success_response("Dynamic fact removed", {"fact_type": fact_type})


# from fastapi import APIRouter
# from app.db.database import SessionLocal
# from app.db.models import DynamicFact, StaticFact, LearnedResponse
# from app.utils.response_format import success_response, error_response
#
# router = APIRouter()
#
# @router.get("/admin/show_dynamic_facts")
# async def show_dynamic_facts():
#     db = SessionLocal()
#     try:
#         facts = db.query(DynamicFact).all()
#         facts_data = [{"fact_type": fact.fact_type, "fact_value": fact.fact_value} for fact in facts]
#         return success_response("Dynamic facts retrieved successfully", {"dynamic_facts": facts_data})
#     except Exception as e:
#         return error_response(f"An error occurred: {str(e)}")
#     finally:
#         db.close()
#
#
@router.delete(
    "/dynamic-facts",
    summary="Delete all dynamic facts",
    description="Remove every dynamic fact from the knowledge base."
)
async def delete_all_dynamics():
    count = delete_all_dynamic_facts()
    if count == 0:
        return success_response("No dynamic facts to delete", {"deleted_count": 0})
    return success_response(f"Deleted {count} dynamic facts", {"deleted_count": count})

# ---------- 1) Delete user-taught Q&A ----------
@router.delete(
    "/learned-responses/{question}",
    summary="Delete a learned response"
)
async def remove_learned(question: str):
    deleted = delete_learned_response(question.lower())
    if not deleted:
        raise HTTPException(404, detail="Learned response not found")
    return success_response("Deleted learned response", {"question": question})


# ---------- 2–4) CRUD for Static Facts ----------
class StaticFactIn(BaseModel):
    pattern:  str
    response: str

@router.get(
    "/static-facts",
    summary="List all static facts"
)
async def list_static():
    items = get_all_static_facts()
    return success_response("Static facts retrieved", {"items": items})


@router.post(
    "/static-facts",
    summary="Add a new static fact"
)
async def add_static(f: StaticFactIn):
    set_static_fact(f.pattern.lower(), f.response)
    return success_response("Static fact added", {"pattern": f.pattern})


@router.put(
    "/static-facts/{pattern}",
    summary="Update an existing static fact"
)
async def update_static(pattern: str, f: StaticFactIn):
    # ensure URL and body match
    if pattern.lower() != f.pattern.lower():
        raise HTTPException(400, detail="Pattern in URL and body must match")
    set_static_fact(f.pattern.lower(), f.response)
    return success_response("Static fact updated", {"pattern": f.pattern})


@router.delete(
    "/static-facts/{pattern}",
    summary="Delete a static fact"
)
async def remove_static(pattern: str):
    deleted = delete_static_fact(pattern.lower())
    if not deleted:
        raise HTTPException(404, detail="Static fact not found")
    return success_response("Static fact deleted", {"pattern": pattern})