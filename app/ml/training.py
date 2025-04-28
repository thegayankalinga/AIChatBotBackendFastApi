# app/ml/training.py

import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from app.ml.nlp_utils import tokenize, stem, bag_of_words
from app.ml.model_neural import NeuralNet
import numpy as np

# Load intents
with open("intents.json", "r") as f:
    intents = json.load(f)

all_words = []
tags = []
xy = []

# Preprocessing
for intent in intents["intents"]:
    tag = intent["tag"]
    tags.append(tag)
    for pattern in intent["patterns"]:
        w = tokenize(pattern)
        all_words.extend(w)
        xy.append((w, tag))

ignore_words = ["?", "!", ".", ","]
all_words = [stem(w) for w in all_words if w not in ignore_words]
all_words = sorted(set(all_words))
tags = sorted(set(tags))

# Create training data
X_train = []
y_train = []

for (pattern_sentence, tag) in xy:
    bag = bag_of_words(pattern_sentence, all_words)
    X_train.append(bag)
    y_train.append(tags.index(tag))

# Convert to numpy array first to avoid the warning
X_train = np.array(X_train, dtype=np.float32)
y_train = np.array(y_train, dtype=np.int64)

# Then convert to tensor
X_train = torch.tensor(X_train)
y_train = torch.tensor(y_train)

# Hyperparameters - increased for better learning
batch_size = 8
hidden_size = 64  # Increased from 8
output_size = len(tags)
input_size = len(all_words)
learning_rate = 0.0005  # Reduced from 0.001
num_epochs = 2000  # Increased from 1000


class ChatDataset(Dataset):
    def __init__(self):
        self.n_samples = len(X_train)
        self.x_data = X_train
        self.y_data = y_train

    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    def __len__(self):
        return self.n_samples


dataset = ChatDataset()
train_loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True)

# Initialize model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = NeuralNet(input_size, hidden_size, output_size).to(device)

# Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

# Learning rate scheduler without verbose parameter
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='min', factor=0.5, patience=50
)

# Training loop with early stopping
best_loss = float('inf')
patience_counter = 0
max_patience = 200

for epoch in range(num_epochs):
    total_loss = 0
    for (words, labels) in train_loader:
        words = words.to(device)
        labels = labels.to(device)

        outputs = model(words)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    avg_loss = total_loss / len(train_loader)
    scheduler.step(avg_loss)

    if (epoch + 1) % 100 == 0:
        print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {avg_loss:.4f}')

    # Early stopping
    if avg_loss < best_loss:
        best_loss = avg_loss
        patience_counter = 0

        # Save the best model
        data = {
            "model_state": model.state_dict(),
            "input_size": input_size,
            "hidden_size": hidden_size,
            "output_size": output_size,
            "all_words": all_words,
            "tags": tags
        }
        torch.save(data, "model.pth")
    else:
        patience_counter += 1
        if patience_counter >= max_patience:
            print(f"Early stopping at epoch {epoch + 1}")
            break

print(f"Final Loss: {best_loss:.4f}")
print("Training complete. File saved to model.pth")