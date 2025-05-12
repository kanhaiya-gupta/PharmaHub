from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.database.database_sqlite import SQLiteDatabase
from datetime import datetime

router = APIRouter(prefix="/stores", tags=["stores"])
templates = Jinja2Templates(directory="templates")

# Dependency to get database instance
def get_db():
    return SQLiteDatabase('medical_store.db')

@router.get("/", response_class=HTMLResponse)
async def list_stores(request: Request, db: SQLiteDatabase = Depends(get_db)):
    stores = db.get_store()
    return templates.TemplateResponse("stores.html", {
        "request": request,
        "stores": stores
    })

@router.post("/add")
async def add_store(
    store_name: str = Form(...),
    address: str = Form(...),
    contact_number: str = Form(...),
    license_number: str = Form(...),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        store_data = {
            "StoreName": store_name,
            "Address": address,
            "ContactNumber": contact_number,
            "LicenseNumber": license_number,
            "OpeningDate": datetime.now().strftime("%Y-%m-%d")
        }
        
        store_id = db.insert_store(store_data)
        if store_id:
            return RedirectResponse(url="/stores", status_code=303)
        else:
            raise HTTPException(status_code=400, detail="Failed to add store")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{store_id}", response_class=HTMLResponse)
async def get_store_dashboard(
    request: Request,
    store_id: int,
    db: SQLiteDatabase = Depends(get_db)
):
    store = db.get_store({"StoreID": store_id})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Get store statistics
    medicines = db.get_medicine({"StoreID": store_id})
    total_medicines = len(medicines)
    low_stock = len([m for m in medicines if m['StockQuantity'] < 10])
    
    return templates.TemplateResponse("store_dashboard.html", {
        "request": request,
        "store": store[0],
        "stats": {
            "total_medicines": total_medicines,
            "low_stock": low_stock
        }
    })

@router.get("/{store_id}/medicines", response_class=HTMLResponse)
async def get_store_medicines(
    request: Request,
    store_id: int,
    db: SQLiteDatabase = Depends(get_db)
):
    medicines = db.get_medicine({"StoreID": store_id})
    return templates.TemplateResponse("store_medicines.html", {
        "request": request,
        "medicines": medicines,
        "store_id": store_id
    })

@router.get("/{store_id}/customers", response_class=HTMLResponse)
async def get_store_customers(
    request: Request,
    store_id: int,
    db: SQLiteDatabase = Depends(get_db)
):
    customers = db.get_customer({"StoreID": store_id})
    return templates.TemplateResponse("store_customers.html", {
        "request": request,
        "customers": customers,
        "store_id": store_id
    })

@router.get("/{store_id}/operators", response_class=HTMLResponse)
async def get_store_operators(
    request: Request,
    store_id: int,
    db: SQLiteDatabase = Depends(get_db)
):
    operators = db.get_operator({"StoreID": store_id})
    return templates.TemplateResponse("store_operators.html", {
        "request": request,
        "operators": operators,
        "store_id": store_id
    })

@router.get("/{store_id}/purchases", response_class=HTMLResponse)
async def get_store_purchases(
    request: Request,
    store_id: int,
    db: SQLiteDatabase = Depends(get_db)
):
    purchases = db.get_purchase({"StoreID": store_id})
    purchase_items = db.get_purchase_item()
    
    # Combine purchase data with related information
    purchase_details = []
    for purchase in purchases:
        customer = db.get_customer({"CustomerID": purchase["CustomerID"]})
        operator = db.get_operator({"OperatorID": purchase["OperatorID"]})
        
        items = [item for item in purchase_items if item["PurchaseID"] == purchase["PurchaseID"]]
        for item in items:
            medicine = db.get_medicine({"MedicineID": item["MedicineID"]})
            
            purchase_details.append({
                "customer": customer[0]["Name"] if customer else "Unknown",
                "medicine": medicine[0]["Name"] if medicine else "Unknown",
                "quantity": item["Quantity"],
                "operator": operator[0]["Name"] if operator else "Unknown",
                "date": purchase["DateOfPurchase"]
            })
    
    return templates.TemplateResponse("store_purchases.html", {
        "request": request,
        "purchases": purchase_details,
        "store_id": store_id
    }) 