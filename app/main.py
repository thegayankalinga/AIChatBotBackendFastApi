import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.context_store import load_history, save_history
from app.db.database import Base, engine, initialize_static_facts, initialize_dynamic_facts
from app.routes import chat, teachme, admin
from app.routes.chat_ws import router as chat_ws_router


HISTORY_FILE = os.path.join(os.path.dirname(__file__), "../history.json")
SECRET_KEY   = "fastapi-local-dev-secret-ai-coursework-cw2"
origins = ["http://localhost:5173",   "https://ai-chatbot-frontend-lrpu.onrender.com"]

middleware = [
    Middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"]),
    Middleware(SessionMiddleware, secret_key=SECRET_KEY),
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup logic ---
    load_history(HISTORY_FILE)
    yield
    # --- shutdown logic ---
    save_history(HISTORY_FILE)

app = FastAPI(
    lifespan=lifespan,
    middleware=middleware)
    # type: ignore[arg-type]
app.include_router(chat_ws_router, prefix="", tags=["Chat WS"])
# CORS Settings
origins = ["http://localhost:5173"]  # Frontend URL

# Initialize Database
Base.metadata.create_all(bind=engine)
initialize_static_facts()
initialize_dynamic_facts()

# Mount each router under its own path so Swagger can discover them
app.include_router(chat.router,    prefix="/chat",    tags=["Chat"])
app.include_router(teachme.router, prefix="/teachme", tags=["TeachMe"])
app.include_router(admin.router,   prefix="/admin",   tags=["Admin"])

@app.get("/")
async def root():
    return {"message": "Welcome to AI Chatbot!"}
