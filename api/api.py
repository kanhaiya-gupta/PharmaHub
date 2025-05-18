# api/api.py
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from .routes import (
    stores_router,
    medicines_router,
    customers_router,
    operators_router,
    purchases_router,
    sync_router,
    reports_router
)
from src.database.database_sqlite import SQLiteDatabase

app = FastAPI(
    title="PharmaHub API",
    description="API for PharmaHub medical store management system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Dependency to get database instance
def get_db():
    return SQLiteDatabase('medical_store.db')

# Root route shows welcome page
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "welcome.html",
        {
            "request": request,
            "title": "Welcome to PharmaHub"
        }
    )

# Data Manager Dashboard
@app.get("/data-manager/dashboard", response_class=HTMLResponse)
async def data_manager_dashboard(request: Request, db: SQLiteDatabase = Depends(get_db)):
    try:
        # Get statistics
        total_stores = len(db.get_store({}))
        total_medicines = len(db.get_medicine({}))
        total_customers = len(db.get_customer({}))
        total_operators = len(db.get_operator({}))
        total_purchases = len(db.get_purchase({}))
        
        # Get recent purchases (get all and slice to get last 5)
        all_purchases = db.get_purchase({})
        recent_purchases = sorted(all_purchases, key=lambda x: x.get('DateOfPurchase', ''), reverse=True)[:5]
        
        # Get low stock medicines
        all_medicines = db.get_medicine({})
        low_stock_medicines = [m for m in all_medicines if m.get('StockQuantity', 0) < 10][:5]
        
        return templates.TemplateResponse(
            "data_manager_dashboard.html",
            {
                "request": request,
                "title": "Data Manager Dashboard",
                "statistics": {
                    "total_stores": total_stores,
                    "total_medicines": total_medicines,
                    "total_customers": total_customers,
                    "total_operators": total_operators,
                    "total_purchases": total_purchases
                },
                "recent_purchases": recent_purchases,
                "low_stock_medicines": low_stock_medicines
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "Error",
                "error_message": str(e)
            }
        )

# Include routers
app.include_router(stores_router)
app.include_router(medicines_router)
app.include_router(customers_router)
app.include_router(operators_router)
app.include_router(purchases_router)
app.include_router(sync_router)
app.include_router(reports_router)
