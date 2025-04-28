# app/services/nlp_service.py

from app.ml.predictor import predict_intent
from app.services.db_service import get_static_response, get_learned_response

CONFIDENCE_THRESHOLD = 0.70  # Adjustable

def generate_response(user_input: str):
    tag, confidence = predict_intent(user_input)

    if confidence > CONFIDENCE_THRESHOLD:
        # Try getting static response
        static_resp = get_static_response(tag)
        if static_resp:
            return static_resp

        # Try getting learned response
        learned_resp = get_learned_response(tag)
        if learned_resp:
            return learned_resp

        return f"I understood your intent '{tag}', but don't have a response configured yet."
    else:
        return "I'm sorry, I didn't understand. Can you rephrase your question?"