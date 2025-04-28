# app/ml/model_loader.py

import pickle
import torch
import nltk
from app.ml.model_neural import NeuralNet
from app.ml.nlp_utils import bag_of_words, tokenize

# Try to ensure NLTK data is available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt')
    except Exception as e:
        print(f"Warning: Could not download NLTK punkt: {e}")

# Paths
MODEL_PATH = "model.pth"
TOKENIZER_PATH = "tokenizer.pkl"


# Load model and tokenizer
def load_model():
    try:
        data = torch.load(MODEL_PATH)

        input_size = data["input_size"]
        hidden_size = data["hidden_size"]
        output_size = data["output_size"]
        all_words = data["all_words"]
        tags = data["tags"]
        model_state = data["model_state"]

        model = NeuralNet(input_size, hidden_size, output_size)
        model.load_state_dict(model_state)
        model.eval()

        return model, all_words, tags
    except Exception as e:
        print(f"Error loading model: {e}")
        # Return empty values that won't crash the app
        return None, [], []


# Load bag of words with improved robustness
def get_bag_of_words(sentence, all_words):
    # Try to tokenize, but have a fallback for simple tokenization
    try:
        tokens = tokenize(sentence)
    except Exception as e:
        print(f"Error in tokenization: {e}")
        # Simple fallback tokenization
        tokens = sentence.lower().split()

    return bag_of_words(tokens, all_words)