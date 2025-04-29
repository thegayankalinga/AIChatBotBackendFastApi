# app/routes/chat.py

import json
import random
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.nlp_service import generate_response  # should accept model_type

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


# Pre-load intent patterns for direct keyword shortcuts
with open("intents.json", "r") as f:
    intents_data = json.load(f)

# Flatten out the greeting & ATM patterns (for quick direct replies)
greeting_patterns = [
    p.lower() for intent in intents_data["intents"]
    if intent["tag"] == "greeting"
    for p in intent["patterns"]
]
atm_patterns = [
    p.lower() for intent in intents_data["intents"]
    if intent["tag"] == "atm_locations"
    for p in intent["patterns"]
]


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    model: str = Query(
        "transformer",
        description="Which model to use: 'ml' for legacy or 'transformer' for BERT",
        enum=["ml", "transformer"]
    )
):
    """
    Chat endpoint. Tries:
     1) Direct ATM keyword reply
     2) Direct greeting reply
     3) Falls back to `generate_response` in nlp_service,
        passing along model_type to choose ML vs Transformer.
    """
    text = request.message.strip()
    lower = text.lower()

    # 1) ATM shortcut (highest priority)
    atm_keywords = ["atm", "bank machine", "cash machine", "nearest", "closest", "location", "near me"]
    if any(kw in lower for kw in atm_keywords):
        # pick a random ATM reply from intents.json
        for intent in intents_data["intents"]:
            if intent["tag"] == "atm_locations":
                return ChatResponse(response=random.choice(intent["responses"]))

    # 2) Simple greeting shortcut
    common_greetings = ["hi", "hello", "hey", "greetings", "hi there", "hello there"]
    if lower in common_greetings:
        greets = [
            "Hello! How can I assist you today?",
            "Hi there! What can I do for you?",
            "Greetings! What brings you here?",
            "Hello! How may I help you?",
            "Hi! How can I be of service?",
        ]
        return ChatResponse(response=random.choice(greets))

    # 3) Full NLU path
    try:
        bot_reply = generate_response(text, model_type=model)
    except Exception as e:
        # bubble up as a 500
        raise HTTPException(status_code=500, detail=f"NLU error: {e}")

    return ChatResponse(response=bot_reply)