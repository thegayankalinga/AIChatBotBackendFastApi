# app/ml/predictor.py

import json
import torch
from transformers import BertTokenizer, BertForSequenceClassification, PreTrainedTokenizer, PreTrainedModel

# 1. Load intents.json to rebuild tag list and pattern matches
with open("intents.json", "r") as f:
    intents_data = json.load(f)

# Build tag ↔ id mapping and pattern dict
intent_to_id = {}
id_to_intent = {}
pattern_to_intent = {}
for idx, intent in enumerate(intents_data["intents"]):
    tag = intent["tag"]
    intent_to_id[tag] = idx
    id_to_intent[idx] = tag
    for pattern in intent["patterns"]:
        p = pattern.lower().strip().rstrip("?!.")
        pattern_to_intent[p] = tag

# 2. Load tokenizer & model from your fine-tuned checkpoint
MODEL_DIR = "saved_intent_model"
tokenizer: PreTrainedTokenizer = BertTokenizer.from_pretrained(MODEL_DIR)
model: PreTrainedModel      = BertForSequenceClassification.from_pretrained(MODEL_DIR)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

# 3. Prediction function
def predict_intent(sentence: str):
    # Normalize
    s = sentence.lower().strip()
    clean = s.rstrip("?!.")

    # 3a. Exact pattern match
    if clean in pattern_to_intent:
        return pattern_to_intent[clean], 1.0

    # 3b. Short greeting override
    if clean in {"hi", "hello", "hey"}:
        return "greeting", 1.0

    # 3c. ATM keyword shortcut
    if any(k in clean for k in ("atm", "cash machine", "nearest", "closest")):
        return "atm_locations", 0.9

    # 3d. Fall back to BERT
    try:
        # Tokenize + move to device
        inputs = tokenizer(
            sentence,
            truncation=True,
            padding="max_length",
            max_length=128,
            return_tensors="pt"
        ).to(device)

        with torch.no_grad():
            outputs = model(**inputs)
        logits = outputs.logits

        probs = torch.nn.functional.softmax(logits, dim=1)[0]
        conf, pred_id = torch.max(probs, dim=0)

        tag = id_to_intent[pred_id.item()]
        return tag, conf.item()

    except Exception as e:
        # If something goes wrong with BERT, fall back on your old keyword logic
        print(f"[predict_intent] BERT error: {e}")
        return _fallback_by_keywords(clean)

# 4. Fallback keyword matcher (same as before)
def _fallback_by_keywords(sentence: str):
    if any(w in sentence for w in ("hi", "hello", "hey")):
        return "greeting", 0.8
    if any(w in sentence for w in ("atm", "cash", "bank", "near", "location")):
        return "atm_locations", 0.8
    if any(w in sentence for w in ("account", "open", "create")):
        return "account_opening", 0.7
    return "greeting", 0.4