# api/api.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .routes import stores, medicines, customers, operators, purchases, sync

app = FastAPI(title="PharmaHub API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(stores.router)
app.include_router(medicines.router)
app.include_router(customers.router)
app.include_router(operators.router)
app.include_router(purchases.router)
app.include_router(sync.router)
