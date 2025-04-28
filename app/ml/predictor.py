# app/ml/predictor.py

import torch
import json
import nltk
from app.ml.model_loader import load_model, get_bag_of_words

# Load intents for direct pattern matching
with open("intents.json", "r") as f:
    intents_data = json.load(f)

# Create pattern to intent mapping for exact matches
pattern_to_intent = {}
for intent in intents_data["intents"]:
    for pattern in intent["patterns"]:
        pattern_lower = pattern.lower().strip()
        # Remove punctuation for better matching
        pattern_lower = pattern_lower.replace('?', '').replace('!', '').replace('.', '').strip()
        pattern_to_intent[pattern_lower] = intent["tag"]

# Load model only once when module is imported
try:
    model, all_words, tags = load_model()
    # Make sure model is in evaluation mode
    if model is not None:
        model.eval()
except Exception as e:
    print(f"Error initializing model: {e}")
    model, all_words, tags = None, [], []


def predict_intent(sentence: str):
    # Clean the input
    sentence = sentence.lower().strip()
    clean_sentence = sentence.replace('?', '').replace('!', '').replace('.', '').strip()

    # Try direct pattern matching first (exact matches)
    if clean_sentence in pattern_to_intent:
        print(f"Exact pattern match found: '{clean_sentence}' -> {pattern_to_intent[clean_sentence]}")
        return pattern_to_intent[clean_sentence], 1.0

    # Special handling for short greetings
    common_greetings = {"hi": "greeting", "hello": "greeting", "hey": "greeting"}
    if clean_sentence in common_greetings:
        print(f"Direct match found for '{clean_sentence}' -> {common_greetings[clean_sentence]}")
        return common_greetings[clean_sentence], 1.0

    # Special handling for ATM-related queries
    atm_keywords = ["atm", "bank machine", "cash machine", "closest", "nearest"]
    if any(keyword in clean_sentence for keyword in atm_keywords):
        print(f"ATM keyword match found in: '{clean_sentence}'")
        return "atm_locations", 0.9

    # Normal prediction flow with error handling
    try:
        if model is None or not all_words:
            print("Model not loaded properly, using fallback")
            # Try to predict based on keywords in the sentence
            return predict_by_keywords(clean_sentence)

        X = get_bag_of_words(sentence, all_words)
        X = torch.from_numpy(X).float()
        X = X.unsqueeze(0)  # batch dimension

        with torch.no_grad():  # Disable gradient calculation for inference
            output = model(X)

        _, predicted = torch.max(output, dim=1)

        if predicted.item() < len(tags):
            tag = tags[predicted.item()]
            probs = torch.softmax(output, dim=1)
            prob = probs[0][predicted.item()]

            # Apply confidence boosting for known patterns
            boosted_confidence = boost_confidence(clean_sentence, tag, prob.item())

            return tag, boosted_confidence
        else:
            print("Prediction index out of range")
            return predict_by_keywords(clean_sentence)
    except Exception as e:
        print(f"Error in prediction: {e}")
        return predict_by_keywords(clean_sentence)


def predict_by_keywords(sentence):
    """Fallback prediction based on keywords"""
    # Check for greeting keywords
    greeting_keywords = ["hi", "hello", "hey", "greetings", "morning", "afternoon", "evening"]
    if any(keyword == sentence or keyword in sentence.split() for keyword in greeting_keywords):
        return "greeting", 0.8

    # Check for ATM/location keywords
    atm_keywords = ["atm", "bank", "machine", "cash", "closest", "nearest", "near", "location"]
    if any(keyword in sentence for keyword in atm_keywords):
        return "atm_locations", 0.8

    # Check for account keywords
    account_keywords = ["account", "savings", "checking", "open", "create", "new account"]
    if any(keyword in sentence for keyword in account_keywords):
        return "account_opening", 0.7

    # Default to greeting with low confidence
    return "greeting", 0.4


def boost_confidence(sentence, predicted_tag, original_confidence):
    """Boost confidence for phrases similar to training data"""
    # Find all patterns for this tag
    patterns = []
    for intent in intents_data["intents"]:
        if intent["tag"] == predicted_tag:
            patterns = [p.lower().strip() for p in intent["patterns"]]
            break

    # Calculate similarity to known patterns
    max_similarity = 0
    for pattern in patterns:
        # Simple word overlap similarity
        pattern_words = set(pattern.split())
        sentence_words = set(sentence.split())
        if len(pattern_words) > 0 and len(sentence_words) > 0:
            overlap = len(pattern_words.intersection(sentence_words))
            similarity = overlap / max(len(pattern_words), len(sentence_words))
            max_similarity = max(max_similarity, similarity)

    # Boost confidence based on similarity to known patterns
    if max_similarity > 0.5:  # If there's significant overlap
        boosted = original_confidence + (max_similarity * 0.5)  # Boost by up to 0.5
        return min(boosted, 0.95)  # Cap at 0.95

    return original_confidence