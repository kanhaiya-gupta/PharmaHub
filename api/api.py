# api/api.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routes import router as api_router

app = FastAPI(title="Medical Store API")

# Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(api_router)
