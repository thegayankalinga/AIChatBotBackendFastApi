# Dockerfile for AIChatBotBackendFastApi

# 1️⃣ Base image
FROM python:3.12-slim AS base
WORKDIR /app

# 2️⃣ Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git \
       curl \
    && rm -rf /var/lib/apt/lists/*

# 3️⃣ Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 4️⃣ Copy application code
COPY . .

# 5️⃣ Download NLTK data
RUN python -m nltk.downloader punkt

# 6️⃣ Build-time training flags (default: skip heavy training)
ARG TRAIN_TRANSFORMER=false
ARG TRAIN_ML=false

# 7️⃣ Conditionally train Transformer model
RUN if [ "$TRAIN_TRANSFORMER" = "true" ]; then \
        echo "🔧 Training Transformer model..." && \
        python training_transformer.py; \
    else \
        echo "🚫 Skipping Transformer training"; \
    fi

# 8️⃣ Conditionally train ML model
RUN if [ "$TRAIN_ML" = "true" ]; then \
        echo "🔧 Training legacy ML model..." && \
        python training.py; \
    else \
        echo "🚫 Skipping ML training"; \
    fi

# 9️⃣ Expose port and default command
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
