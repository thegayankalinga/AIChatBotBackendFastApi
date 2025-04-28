# app/routes/chat.py

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.nlp_service import generate_response
from app.utils.response_format import success_response

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat_with_bot(chat_request: ChatRequest):
    user_message = chat_request.message
    response = generate_response(user_message)
    return success_response("Response generated successfully", {"response": response})