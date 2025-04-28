# app/services/nlp_service.py

import random
import json
from app.ml.predictor import predict_intent
from app.services.db_service import get_static_response, get_learned_response

# Load intents for fallback
with open("intents.json", "r") as f:
    intents_data = json.load(f)

CONFIDENCE_THRESHOLD = 0.10  # Lowered from 0.35


def generate_response(user_input: str):
    tag, confidence = predict_intent(user_input)

    print(f"PREDICTED: tag={tag}, confidence={confidence:.2f}")

    # Check for exact greeting matches only - no partial matches
    user_input_lower = user_input.lower().strip()
    exact_greetings = ["hi", "hello", "hey", "greetings", "morning", "evening", "afternoon",
                       "good morning", "good evening", "good afternoon"]

    # Only classify as a greeting if it's an exact match or very short
    if user_input_lower in exact_greetings or (
            len(user_input_lower.split()) <= 2 and any(g == user_input_lower for g in exact_greetings)):
        # Try getting static response for greeting
        static_resp = get_static_response("greeting")
        if static_resp:
            return static_resp

        # Fallback to intents.json
        for intent in intents_data["intents"]:
            if intent["tag"] == "greeting":
                return random.choice(intent["responses"])

    # Check for ATM/banking keywords to prevent misclassification
    atm_keywords = ["atm", "bank", "cash", "machine", "closest", "nearest", "location", "near me"]
    if any(keyword in user_input_lower for keyword in atm_keywords) and "atm_locations" in [intent["tag"] for intent in
                                                                                            intents_data["intents"]]:
        # Try getting static response for ATM locations
        static_resp = get_static_response("atm_locations")
        if static_resp:
            return static_resp

        # Fallback to intents.json
        for intent in intents_data["intents"]:
            if intent["tag"] == "atm_locations":
                return random.choice(intent["responses"])

    # Continue with normal flow if not a greeting or ATM request, or if those checks didn't return
    if confidence > CONFIDENCE_THRESHOLD:
        # Try getting static response
        static_resp = get_static_response(tag)
        if static_resp:
            return static_resp

        # Try getting learned response
        learned_resp = get_learned_response(tag)
        if learned_resp:
            return learned_resp

        # Fallback to intents.json if no database response
        for intent in intents_data["intents"]:
            if intent["tag"] == tag:
                return random.choice(intent["responses"])

        return f"I understood your intent '{tag}', but don't have a response configured yet."
    else:
        return "I'm sorry, I didn't understand. Can you rephrase your question?"