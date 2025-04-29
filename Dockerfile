# Stage 1: clone + pull LFS
FROM alpine/git AS fetcher
RUN apk add --no-cache git-lfs
WORKDIR /repo

# Use build-args for private repos if needed:
ARG GIT_URL="https://github.com/your-org/your-repo.git"
ARG GIT_REF="HEAD"
RUN git clone "$GIT_URL" . \
 && git -c protocol.version=2 lfs install \
 && git lfs pull --include="saved_intent_model/*" \
 && git checkout "$GIT_REF"

# Stage 2: build your Python app
FROM python:3.12-slim
WORKDIR /app

# Copy only the model directory from the fetcher
COPY --from=fetcher /repo/saved_intent_model ./saved_intent_model

# Install deps
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# Copy the rest of your code
COPY . .

# Download NLTK data
RUN python -m nltk.downloader punkt

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]