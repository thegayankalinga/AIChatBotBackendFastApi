# app/routes/chat.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import random
import json

from app.services.nlp_service import generate_response

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


# Load intents for keyword matching
with open("intents.json", "r") as f:
    intents_data = json.load(f)

# Create keyword maps for direct matching
greeting_patterns = []
atm_patterns = []
# Extract patterns from intents
for intent in intents_data["intents"]:
    if intent["tag"] == "greeting":
        greeting_patterns = [p.lower() for p in intent["patterns"]]
    elif intent["tag"] == "atm_locations":
        atm_patterns = [p.lower() for p in intent["patterns"]]


@router.post("/")
async def chat(request: ChatRequest):
    message = request.message.strip()
    lower_message = message.lower()

    # ATM/banking keyword detection (higher priority than greetings)
    atm_keywords = ["atm", "bank machine", "cash machine", "closest", "nearest", "location", "near me"]

    if any(keyword in lower_message for keyword in atm_keywords):
        for intent in intents_data["intents"]:
            if intent["tag"] == "atm_locations":
                return ChatResponse(response=random.choice(intent["responses"]))

    # Direct handling for common greetings
    common_greetings = ["hi", "hello", "hey", "hello there", "hi there", "greetings"]

    if lower_message in common_greetings:
        greeting_responses = [
            "Hello! How can I assist you today?",
            "Hi there! What can I do for you?",
            "Greetings! What brings you here?",
            "Hello! How may I help you?",
            "Hi! How can I be of service?",
        ]
        return ChatResponse(response=random.choice(greeting_responses))

    # Normal processing for other messages
    response = generate_response(message)
    return ChatResponse(response=response)