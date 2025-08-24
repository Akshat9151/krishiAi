# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router        # routes.py se import
from services import auth        # services/auth.py se import
from services.utils import run_migrations

# FastAPI app initialization
app = FastAPI(
    title="Krishi AI",
    description="Crop Recommendation System",
    version="1.0"
)

# CORS Middleware (frontend ke liye)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Specific domains: ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes include karna
app.include_router(router)       # General routes (routes.py)
app.include_router(auth.router)  # Authentication routes (services/auth.py)

# Root endpoint (testing)
@app.get("/")
def home():
    return {"message": "🚀 Welcome to Krishi AI API – Crop Recommendation System"}

# Initialize DB schema on startup (graceful if DB not available)
@app.on_event("startup")
def startup_event():
    try:
        run_migrations()
    except Exception as exc:
        print(f"[startup] DB migration skipped due to error: {exc}")
