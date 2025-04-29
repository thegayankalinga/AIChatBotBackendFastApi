# Use an official Python runtime
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# 1. Install build-time deps and Python packages
#    – we install huggingface_hub so we can fetch the model
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt \
 && pip install huggingface_hub

# 2. Download your model into saved_intent_model/
#    Replace the HF_REPO, FILENAME and (optionally) HF_TOKEN with your values.
#    If you host elsewhere, swap this for a `wget` or `curl` command.
ARG HF_REPO="your-username/intent-model-repo"
ARG FILENAME="model.safetensors"
# If your repo is private, also pass in HF_TOKEN at build time:
#   docker build --build-arg HF_TOKEN=<your_token> .
ARG HF_TOKEN
RUN python - << 'EOF'
import os
from huggingface_hub import hf_hub_download

os.makedirs("saved_intent_model", exist_ok=True)
hf_hub_download(
    repo_id=os.getenv("HF_REPO"),
    filename=os.getenv("FILENAME"),
    cache_dir="saved_intent_model",
    token=os.getenv("HF_TOKEN", None)
)
EOF

# 3. Copy the rest of your application code
COPY . .

# 4. Fetch NLTK data
RUN python -m nltk.downloader punkt

# 5. Expose and run
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]