# api/api.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from .routes import router as api_router

app = FastAPI(title="Medical Store API")

# Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja templates directory
templates = Jinja2Templates(directory="templates")

# Include API routes
app.include_router(api_router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/customers", response_class=HTMLResponse)
async def get_customers(request: Request):
    return templates.TemplateResponse("customers.html", {"request": request})

@app.get("/operators", response_class=HTMLResponse)
async def get_operators(request: Request):
    return templates.TemplateResponse("operators.html", {"request": request})

@app.get("/medicines", response_class=HTMLResponse)
async def get_medicines(request: Request):
    return templates.TemplateResponse("medicines.html", {"request": request})

@app.get("/purchases", response_class=HTMLResponse)
async def get_purchases(request: Request):
    return templates.TemplateResponse("purchases.html", {"request": request})
