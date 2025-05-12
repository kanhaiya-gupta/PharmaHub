from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.database.database_sqlite import SQLiteDatabase
from datetime import datetime

router = APIRouter(prefix="/medicines", tags=["medicines"])
templates = Jinja2Templates(directory="templates")

# Dependency to get database instance
def get_db():
    return SQLiteDatabase('medical_store.db')

@router.get("/", response_class=HTMLResponse)
async def list_medicines(
    request: Request,
    store_id: int = None,
    db: SQLiteDatabase = Depends(get_db)
):
    filter_dict = {"StoreID": store_id} if store_id else {}
    medicines = db.get_medicine(filter_dict)
    return templates.TemplateResponse("medicines.html", {
        "request": request,
        "medicines": medicines,
        "store_id": store_id
    })

@router.post("/add")
async def add_medicine(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    expiry_date: str = Form(...),
    store_id: int = Form(...),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        medicine_data = {
            "Name": name,
            "Description": description,
            "Price": price,
            "StockQuantity": stock_quantity,
            "ExpiryDate": expiry_date,
            "StoreID": store_id
        }
        
        medicine_id = db.insert_medicine(medicine_data)
        if medicine_id:
            return RedirectResponse(url=f"/medicines?store_id={store_id}", status_code=303)
        else:
            raise HTTPException(status_code=400, detail="Failed to add medicine")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch/add")
async def add_batch_medicines(
    medicines: str = Form(...),  # JSON string of medicines
    store_id: int = Form(...),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        import json
        medicine_list = json.loads(medicines)
        
        for medicine in medicine_list:
            medicine["StoreID"] = store_id
            db.insert_medicine(medicine)
            
        return RedirectResponse(url=f"/medicines?store_id={store_id}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{medicine_id}/update")
async def update_medicine(
    medicine_id: int,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    expiry_date: str = Form(...),
    store_id: int = Form(...),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        medicine_data = {
            "Name": name,
            "Description": description,
            "Price": price,
            "StockQuantity": stock_quantity,
            "ExpiryDate": expiry_date
        }
        
        success = db.update_medicine(medicine_id, medicine_data)
        if success:
            return RedirectResponse(url=f"/medicines?store_id={store_id}", status_code=303)
        else:
            raise HTTPException(status_code=400, detail="Failed to update medicine")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{medicine_id}/delete")
async def delete_medicine(
    medicine_id: int,
    store_id: int = Form(...),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        success = db.delete_medicine(medicine_id)
        if success:
            return RedirectResponse(url=f"/medicines?store_id={store_id}", status_code=303)
        else:
            raise HTTPException(status_code=400, detail="Failed to delete medicine")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/low-stock", response_class=HTMLResponse)
async def get_low_stock_medicines(
    request: Request,
    store_id: int = None,
    threshold: int = 10,
    db: SQLiteDatabase = Depends(get_db)
):
    filter_dict = {"StoreID": store_id} if store_id else {}
    medicines = db.get_medicine(filter_dict)
    low_stock = [m for m in medicines if m['StockQuantity'] < threshold]
    
    return templates.TemplateResponse("low_stock_medicines.html", {
        "request": request,
        "medicines": low_stock,
        "store_id": store_id,
        "threshold": threshold
    })

@router.get("/expiring", response_class=HTMLResponse)
async def get_expiring_medicines(
    request: Request,
    store_id: int = None,
    days: int = 30,
    db: SQLiteDatabase = Depends(get_db)
):
    filter_dict = {"StoreID": store_id} if store_id else {}
    medicines = db.get_medicine(filter_dict)
    
    today = datetime.now()
    expiring = []
    for medicine in medicines:
        expiry_date = datetime.strptime(medicine['ExpiryDate'], "%Y-%m-%d")
        days_until_expiry = (expiry_date - today).days
        if 0 <= days_until_expiry <= days:
            medicine['days_until_expiry'] = days_until_expiry
            expiring.append(medicine)
    
    return templates.TemplateResponse("expiring_medicines.html", {
        "request": request,
        "medicines": expiring,
        "store_id": store_id,
        "days": days
    }) 