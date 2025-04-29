from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine, initialize_static_facts
from app.routes import chat, teachme, admin

app = FastAPI()

# CORS Settings
origins = ["http://localhost:5173"]  # Frontend URL

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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