# app/ml/predictor.py

import torch
from app.ml.model_loader import load_model, get_bag_of_words

model, all_words, tags = load_model()

def predict_intent(sentence: str):
    sentence = sentence.lower()
    X = get_bag_of_words(sentence, all_words)
    X = torch.from_numpy(X).float()
    X = X.unsqueeze(0)  # batch dimension

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    return tag, prob.item()