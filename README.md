# AI Chatbot with FastAPI

This project implements a three‑tier chatbot using FastAPI, featuring:

- **Natural Language Interface**: Text-based HTTP and WebSocket endpoints
- **Inference Engine**: Legacy keyword/ML fallback and Transformer‑based intent classification
- **Knowledge Base**: Static facts (intents.json), dynamic facts via SQL database, plus auto‑reloading
- **Session & Context**: Per‑user session cookies with multi‑turn history
- **Streaming Responses**: WebSocket endpoint with typing indicators and partial replies

---

## 📦 Prerequisites

- Python 3.10 or higher
- Git
- [Optional] Hugging Face account & token (if using private HF models)

---

## 🚀 Quick Start

1. **Clone & enter**
   ```bash
   git clone https://github.com/thegayankalinga/AIChatBotBackendFastApi
   cd chatbot_fastapi
   ```

2. **Create virtualenv & install**
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # on Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   Create a `.env` in project root:
   ```ini
   SESSION_SECRET=your_random_secret_here
   HF_TOKEN=your_hf_token_if_private
   ```

4. **Initialize database** (SQLite by default)
   ```bash
   python - << 'EOF'
   from app.db.database import Base, engine, initialize_static_facts, initialize_dynamic_facts
   Base.metadata.create_all(bind=engine)
   initialize_static_facts()
   initialize_dynamic_facts()
   EOF
   ```

5. **Train the models**

   - **Transformer model**:
     ```bash
     python training_transformer.py
     ```
     This fine‑tunes BERT on your `intents.json` data and saves to `saved_intent_model/`.

   - **Legacy ML model**:
     - The default ML fallback is keyword‑based (no training needed).
     - To build a scikit‑learn classifier, create `training_ml.py`, train on `intents.json`, and save to `saved_ml_model/`.

6. **Run the server**
   ```bash
    uvicorn app.main:app --reload
    ```

### 🐳 Docker Deployment

You can build and run the backend in a Docker container:

```bash
# Build the Docker image (replace tag as desired)
docker build -t aichatbot-backend .

# Run the container (map port 8000, mount history.json for persistence)
docker run -d --name aichatbot \
  -p 8000:8000 \
  -e SESSION_SECRET=your_secret \
  -e HF_TOKEN=your_hf_token \
  -v $(pwd)/history.json:/app/history.json \
  aichatbot-backend

# Stream logs
docker logs -f aichatbot

# Stop and remove
docker stop aichatbot && docker rm aichatbot
```


   - HTTP docs: http://127.0.0.1:8000/docs
   - Root welcome: http://127.0.0.1:8000/

---

## 🔧 Configuration & Environment

| Variable         | Description                                     | Default             |
|------------------|-------------------------------------------------|---------------------|
| SESSION_SECRET   | Secret key for signing session cookies          | (see `.env`)        |
| HF_TOKEN         | HF token for private model access               | —                   |
| DATABASE_URL     | SQLAlchemy DB URL (e.g. `sqlite:///./db.sqlite`)| `sqlite:///./db.sqlite` |

---

## 📝 HTTP API

### POST `/chat/`

Send a JSON body:
```json
{ "message": "Hello" }
```
Query params:
- `model`: `ml` or `transformer` (default: `transformer`)

Response:
```json
{ "response": "Bot reply text" }
```

### GET `/chat/session-info`
(Development only) Returns current session ID & history:
```json
{ "session_id": "...", "history": [["user","..."], "..."] }
```

---

## 📡 WebSocket API

**Endpoint**: `ws://127.0.0.1:8000/chat/ws?model=transformer`

**Send** (JSON or raw text):
```json
{"message":"Hi"}
```

**Receive** stream of JSON frames:
```text

{ "type":"typing" }
{ "type":"message", "content":"Hello! " }
{ "type":"message", "content":"How can I assist? " }
{ "type":"done" }

```

### Testing with wscat

#### macOS / Linux
```bash
# install wscat globally via npm
npm install -g wscat
# connect to the WebSocket endpoint\ nwscat -c "ws://127.0.0.1:8000/chat/ws?model=transformer"
```

#### Windows (PowerShell)
```powershell
# install wscat globally via npm
npm install -g wscat
# connect to the WebSocket endpoint
wscat -c "ws://127.0.0.1:8000/chat/ws?model=transformer"
```
bash
# install wscat if needed
npm install -g wscat

# connect
wscat -c "ws://127.0.0.1:8000/chat/ws?model=transformer"
> {"message":"Hello"}
```

---

## 🔄 Hot‑Reloading Intents

Any changes to `intents.json` are auto‑reloaded at runtime (via `watchdog`). No server restart needed.

---

## 📁 Project Structure

```
chatbot_fastapi/
├── app/
│   ├── main.py               # FastAPI app + middleware + routes
│   ├── context_store.py      # session‑history store + persistence
│   ├── routes/
│   │   ├── chat.py           # HTTP chat endpoint
│   │   ├── chat_ws.py        # WebSocket streaming endpoint
│   │   └── teachme.py        # (example extra route)
│   ├── services/
│   │   ├── nlp_service.py    # generate_response logic
│   │   └── db_service.py     # static/dynamic response queries
│   ├── db/
│   │   ├── database.py       # SQLAlchemy base & engine
│   │   └── models.py         # ORM models
│   ├── transformer/
│   │   ├── predictor_transformer.py  # BERT inferencing
│   │   └── training_transformer.py   # BERT fine‑tuning script
│   └── utils/
│       └── model_selector.py # chooses ML vs Transformer
├── intents.json              # static intent patterns & templates
├── requirements.txt          # minimal dependencies
└── README.md                 # this file
```

---

## ⚙️ License

MIT License. Feel free to adapt and extend!

