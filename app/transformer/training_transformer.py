import os
import random
import json
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, random_split
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    DataCollatorWithPadding,
    get_linear_schedule_with_warmup
)
from torch.optim import AdamW
from sklearn.metrics import classification_report

# 1. Reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

# 2. Load intents.json
with open("intents.json", "r") as f:
    intents_data = json.load(f)

# 3. Build texts, labels, and mapping
texts, labels = [], []
intent_to_id = {}
for idx, intent in enumerate(intents_data["intents"]):
    intent_to_id[intent["tag"]] = idx
    for pattern in intent["patterns"]:
        texts.append(pattern)
        labels.append(idx)

# 4. Tokenizer and model
MODEL_NAME = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
model = BertForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(intent_to_id)
)

# 5. Dataset class
class IntentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.tokenizer = tokenizer
        self.texts = texts
        self.labels = labels
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.texts[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )
        item = {k: v.squeeze(0) for k, v in encoding.items()}
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

# 6. Create dataset and splits (80% train, 10% val, 10% test)
dataset = IntentDataset(texts, labels, tokenizer)
train_size = int(0.8 * len(dataset))
val_size   = int(0.1 * len(dataset))
test_size  = len(dataset) - train_size - val_size

train_ds, val_ds, test_ds = random_split(dataset, [train_size, val_size, test_size])

# 7. DataLoaders with dynamic padding
collator = DataCollatorWithPadding(tokenizer=tokenizer)
train_loader = DataLoader(train_ds, batch_size=16, shuffle=True, collate_fn=collator)
val_loader   = DataLoader(val_ds,   batch_size=32, shuffle=False, collate_fn=collator)
test_loader  = DataLoader(test_ds,  batch_size=32, shuffle=False, collate_fn=collator)

# 8. Training setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
optimizer = AdamW(model.parameters(), lr=2e-5)
total_steps = len(train_loader) * 5  # epochs=5
scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=int(0.1 * total_steps),
    num_training_steps=total_steps
)

# 9. Training & evaluation functions
def train_epoch(model, loader):
    model.train()
    total_loss = 0
    for batch in loader:
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model(**batch)
        loss = outputs.loss
        total_loss += loss.item()
        loss.backward()
        optimizer.step()
        scheduler.step()
        optimizer.zero_grad()
    return total_loss / len(loader)

def evaluate(model, loader):
    model.eval()
    all_preds, all_labels = [], []

    with torch.no_grad():
        for batch in loader:
            labels = batch["labels"].to(device)
            inputs = { k:v.to(device)
                       for k,v in batch.items() if k != "labels" }
            logits = model(**inputs).logits
            preds = logits.argmax(dim=1)

            all_preds.extend(preds.cpu().tolist())
            all_labels.extend(labels.cpu().tolist())

    # --- FIX: explicitly pass the full label set and names ---
    labels_list  = list(range(len(intent_to_id)))   # [0,1,...,11]
    target_names = list(intent_to_id.keys())       # your 12 intent tags

    report = classification_report(
        all_labels,
        all_preds,
        labels=labels_list,
        target_names=target_names,
        zero_division=0
    )
    return report

# 10. Main training loop
EPOCHS = 5
for epoch in range(1, EPOCHS + 1):
    train_loss = train_epoch(model, train_loader)
    val_report = evaluate(model, val_loader)
    print(f"\nEpoch {epoch}/{EPOCHS}")
    print(f"  ▶ Train Loss: {train_loss:.4f}")
    print("  ▶ Val Classification Report:\n", val_report)

# 11. Final test evaluation
print("=== Final Test Set Evaluation ===")
test_report = evaluate(model, test_loader)
print(test_report)

# 12. Save fine-tuned model & tokenizer
OUTPUT_DIR = "saved_intent_model"
os.makedirs(OUTPUT_DIR, exist_ok=True)
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"Model and tokenizer saved to `{OUTPUT_DIR}/`")