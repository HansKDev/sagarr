from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from . import models
from .routers import auth, admin

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sagarr API", version="0.1.0")

# Configure CORS
origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",  # React default
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin.router)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "Sagarr Backend", "database": "connected"}
