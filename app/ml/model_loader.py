# app/ml/model_loader.py

import pickle
import torch
from app.ml.model_neural import NeuralNet
from app.ml.nlp_utils import bag_of_words


# Paths
MODEL_PATH = "model.pth"
TOKENIZER_PATH = "tokenizer.pkl"

# Load model and tokenizer
def load_model():
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

# Load bag of words
def get_bag_of_words(sentence, all_words):
    return bag_of_words(sentence, all_words)