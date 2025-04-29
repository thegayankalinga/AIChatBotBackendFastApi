import random
import json

from sqlalchemy.orm import Session

from app.utils.model_selector import predict_intent
from app.services.db_service import (
    get_static_response,
    get_learned_response,
    get_dynamic_fact
)

# Load intents for fallback
with open("intents.json", "r") as f:
    intents_data = json.load(f)

CONFIDENCE_THRESHOLD = 0.10  # Lowered from 0.35


def generate_response(
        user_input: str,
        model_type: str = "transformer") -> str:
    tag, confidence = predict_intent(user_input, model_type=model_type)
    print(f"PREDICTED: tag={tag}, confidence={confidence:.2f}, model={model_type}")

    # 1) Exact greeting shortcut
    u = user_input.lower().strip()
    greetings = ["hi","hello","hey","greetings","good morning","good afternoon","good evening"]
    if u in greetings:
        return get_static_response("greeting") or random.choice(
            next(i["responses"] for i in intents_data["intents"] if i["tag"]=="greeting")
        )

    # 2) ATM shortcut
    if any(k in u for k in ["atm","bank","cash","nearest","closest","location"]):
        return get_static_response("atm_locations") or random.choice(
            next(i["responses"] for i in intents_data["intents"] if i["tag"]=="atm_locations")
        )

    # 3) Dynamic fact override
    dynamic = get_dynamic_fact(tag)
    if dynamic:
        return dynamic

    # 4) Learned / static / fallback
    if confidence > CONFIDENCE_THRESHOLD:
        if (s:=get_static_response(tag)):
            return s
        if (l:=get_learned_response(tag)):
            return l
        return random.choice(
            next(i["responses"] for i in intents_data["intents"] if i["tag"]==tag)
        )
    return "I'm sorry, I didn't understand. Can you rephrase?"


# def generate_response(user_input: str, model_type: str = "transformer") -> str:
#     """
#     Generate a bot response using either the legacy ML or Transformer-based model.
#     """
#     # Use selector to choose the appropriate predictor
#     tag, confidence = predict_intent(user_input, model_type=model_type)
#
#     print(f"PREDICTED: tag={tag}, confidence={confidence:.2f}, model={model_type}")
#
#     # Exact greeting matches (no partials)
#     user_input_lower = user_input.lower().strip()
#     exact_greetings = [
#         "hi", "hello", "hey", "greetings", "morning", "evening", "afternoon",
#         "good morning", "good evening", "good afternoon"
#     ]
#
#     if user_input_lower in exact_greetings or (
#         len(user_input_lower.split()) <= 2 and user_input_lower in exact_greetings
#     ):
#         static_resp = get_static_response("greeting")
#         if static_resp:
#             return static_resp
#         # Fallback to intents.json
#         for intent in intents_data["intents"]:
#             if intent["tag"] == "greeting":
#                 return random.choice(intent["responses"])
#
#     # ATM/banking keyword detection
#     atm_keywords = ["atm", "bank", "cash", "machine", "closest", "nearest", "location", "near me"]
#     if any(kw in user_input_lower for kw in atm_keywords):
#         static_resp = get_static_response("atm_locations")
#         if static_resp:
#             return static_resp
#         for intent in intents_data["intents"]:
#             if intent["tag"] == "atm_locations":
#                 return random.choice(intent["responses"])
#
#     # Use predicted tag if confident
#     if confidence > CONFIDENCE_THRESHOLD:
#         static_resp = get_static_response(tag)
#         if static_resp:
#             return static_resp
#         learned_resp = get_learned_response(tag)
#         if learned_resp:
#             return learned_resp
#         for intent in intents_data["intents"]:
#             if intent["tag"] == tag:
#                 return random.choice(intent["responses"])
#
#         return f"I understood your intent '{tag}', but don't have a response configured yet."
#     else:
#         return "I'm sorry, I didn't understand. Can you rephrase your question?"
