# # app/routes/chat.py


import os
import json
import random
import uuid
from collections import defaultdict
from typing import List, Tuple

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, validator, Field
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.context_store import CONTEXT_STORE
from app.services.nlp_service import generate_response

# Path to the intents file (adjust as needed)
INTENTS_PATH = os.path.join(os.path.dirname(__file__), "../../intents.json")

# Variables to cache intent shortcuts
greeting_patterns: List[str] = []
greeting_responses: List[str] = []
atm_responses:    List[str] = []
atm_keywords:     List[str] = ["atm", "bank machine", "cash machine", "nearest", "closest", "location", "near me"]

# Function to load and cache intents from JSON
def load_intents():
    global greeting_patterns, greeting_responses, atm_responses
    try:
        with open(INTENTS_PATH, "r") as f:
            data = json.load(f)["intents"]
    except Exception as e:
        print(f"Error loading intents.json: {e}")
        return

    # Extract the greeting and ATM intents
    greeting_intent = next((i for i in data if i.get("tag") == "greeting"), None)
    atm_intent      = next((i for i in data if i.get("tag") == "atm_locations"), None)

    if greeting_intent:
        greeting_patterns  = [p.lower() for p in greeting_intent.get("patterns", [])]
        greeting_responses = greeting_intent.get("responses", [])
    if atm_intent:
        atm_responses      = atm_intent.get("responses", [])

    print("[Intents] reloaded greeting and ATM shortcuts.")

# File system event handler to watch for changes to intents.json
class IntentsFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("intents.json"):
            load_intents()


# Bootstrap: load intents and start watcher
load_intents()
observer = Observer()
# Watch the directory containing the intents file
watch_dir = os.path.dirname(INTENTS_PATH)
observer.schedule(IntentsFileHandler(), path=watch_dir, recursive=False)
observer.daemon = True
observer.start()

# Create the router
router = APIRouter()

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500, description="User's message")

    @validator('message')
    def sanitize_message(cls, v: str) -> str:
        # Trim whitespace
        v = v.strip()
        # Remove non-printable characters
        return ''.join(ch for ch in v if ch.isprintable())

class ChatResponse(BaseModel):
    response: str


@router.get("/session-info")
async def session_info(request: Request):
    sid = request.session.get("id")
    return {
        "session_id": sid,
        "history": CONTEXT_STORE.get(sid, [])
    }

@router.post("/", response_model=ChatResponse)
async def chat(
    chat_req: ChatRequest,
    request: Request,
    model: str = Query(
        "transformer",
        description="Which model to use: 'ml' or 'transformer'",
        enum=["ml", "transformer"]
    )
):
    # Parse message
    #body = await request.json()
    message = chat_req.message
    lower   = message.lower()

    # Ensure session ID
    session_id = request.session.get("id")
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session["id"] = session_id

    # Retrieve history and append user turn
    history = CONTEXT_STORE[session_id]
    history.append(("user", message))
    if len(history) > 20:
        history.pop(0)

    # Shortcut: ATM questions
    if any(kw in lower for kw in atm_keywords):
        reply = random.choice(atm_responses) if atm_responses else "I can’t find ATM locations right now."
        history.append(("bot", reply))
        return ChatResponse(response=reply)

    # Shortcut: simple greetings
    if lower in greeting_patterns:
        reply = random.choice(greeting_responses) if greeting_responses else "Hello! How can I help?"
        history.append(("bot", reply))
        return ChatResponse(response=reply)

    # NLU fallback
    try:
        bot_reply = await generate_response(
            message    = message,
            model_type = model,
            context    = history
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NLU error: {e}")

    history.append(("bot", bot_reply))
    return ChatResponse(response=bot_reply)

#
#
# import json
# import random
# from fastapi import APIRouter, HTTPException, Query, Request
# from pydantic import BaseModel
# import uuid
#
# from app.services.nlp_service import generate_response  # should accept model_type
# from app.context_store import CONTEXT_STORE
# router = APIRouter()
#
#
# class ChatRequest(BaseModel):
#     message: str
#
#
# class ChatResponse(BaseModel):
#     response: str
#
#
# # Pre-load intent patterns for direct keyword shortcuts
# with open("intents.json", "r") as f:
#     intents_data = json.load(f)
#
# # Flatten out the greeting & ATM patterns (for quick direct replies)
# greeting_patterns = [
#     p.lower() for intent in intents_data["intents"]
#     if intent["tag"] == "greeting"
#     for p in intent["patterns"]
# ]
# atm_patterns = [
#     p.lower() for intent in intents_data["intents"]
#     if intent["tag"] == "atm_locations"
#     for p in intent["patterns"]
# ]
#
#
# @router.post("/", response_model=ChatResponse)
# async def chat(
#     #request: ChatRequest,
#     request: Request,
#     model: str = Query(
#         "transformer",
#         description="Which model to use: 'ml' for legacy or 'transformer' for BERT",
#         enum=["ml", "transformer"]
#     )
# ):
#     """
#     Chat endpoint. Tries:
#      1) Direct ATM keyword reply
#      2) Direct greeting reply
#      3) Falls back to `generate_response` in nlp_service,
#         passing along model_type to choose ML vs Transformer.
#     """
#     # text = request.message.strip()
#     body = await request.json()
#     text = body["message"].strip()
#     lower = text.lower()
#
#
#
#     # 1) ATM shortcut (highest priority)
#     atm_keywords = ["atm", "bank machine", "cash machine", "nearest", "closest", "location", "near me"]
#     if any(kw in lower for kw in atm_keywords):
#         # pick a random ATM reply from intents.json
#         for intent in intents_data["intents"]:
#             if intent["tag"] == "atm_locations":
#                 return ChatResponse(response=random.choice(intent["responses"]))
#
#     # 2) Simple greeting shortcut
#     common_greetings = ["hi", "hello", "hey", "greetings", "hi there", "hello there"]
#     if lower in common_greetings:
#         greets = [
#             "Hello! How can I assist you today?",
#             "Hi there! What can I do for you?",
#             "Greetings! What brings you here?",
#             "Hello! How may I help you?",
#             "Hi! How can I be of service?",
#         ]
#         return ChatResponse(response=random.choice(greets))
#
#     # 3) Full NLU path
#     try:
#         #bot_reply = generate_response(text, model_type=model)
#         bot_reply = await generate_response(
#             message = text,
#             model_type = model,
#             context = history
#         )
#     except Exception as e:
#         # bubble up as a 500
#         raise HTTPException(status_code=500, detail=f"NLU error: {e}")
#
#     history.append(text)
#     return ChatResponse(response=bot_reply)