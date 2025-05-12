from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.database.database_sqlite import SQLiteDatabase

router = APIRouter(prefix="/customers", tags=["customers"])
templates = Jinja2Templates(directory="templates")

# Dependency to get database instance
def get_db():
    return SQLiteDatabase('medical_store.db')

@router.get("/", response_class=HTMLResponse)
async def list_customers(
    request: Request,
    store_id: int = None,
    db: SQLiteDatabase = Depends(get_db)
):
    filter_dict = {"StoreID": store_id} if store_id else {}
    customers = db.get_customer(filter_dict)
    return templates.TemplateResponse("customers.html", {
        "request": request,
        "customers": customers,
        "store_id": store_id
    })

@router.post("/add")
async def add_customer(
    name: str = Form(...),
    contact_number: str = Form(...),
    email: str = Form(...),
    address: str = Form(...),
    store_id: int = Form(...),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        customer_data = {
            "Name": name,
            "ContactNumber": contact_number,
            "Email": email,
            "Address": address,
            "StoreID": store_id
        }
        
        customer_id = db.insert_customer(customer_data)
        if customer_id:
            return RedirectResponse(url=f"/customers?store_id={store_id}", status_code=303)
        else:
            raise HTTPException(status_code=400, detail="Failed to add customer")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{customer_id}/update")
async def update_customer(
    customer_id: int,
    name: str = Form(...),
    contact_number: str = Form(...),
    email: str = Form(...),
    address: str = Form(...),
    store_id: int = Form(...),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        customer_data = {
            "Name": name,
            "ContactNumber": contact_number,
            "Email": email,
            "Address": address
        }
        
        success = db.update_customer(customer_id, customer_data)
        if success:
            return RedirectResponse(url=f"/customers?store_id={store_id}", status_code=303)
        else:
            raise HTTPException(status_code=400, detail="Failed to update customer")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{customer_id}/delete")
async def delete_customer(
    customer_id: int,
    store_id: int = Form(...),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        success = db.delete_customer(customer_id)
        if success:
            return RedirectResponse(url=f"/customers?store_id={store_id}", status_code=303)
        else:
            raise HTTPException(status_code=400, detail="Failed to delete customer")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{customer_id}/history", response_class=HTMLResponse)
async def get_customer_history(
    request: Request,
    customer_id: int,
    store_id: int = None,
    db: SQLiteDatabase = Depends(get_db)
):
    # Get customer details
    customer = db.get_customer({"CustomerID": customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get purchase history
    purchases = db.get_purchase({"CustomerID": customer_id})
    purchase_items = db.get_purchase_item()
    
    # Combine purchase data with medicine information
    purchase_history = []
    for purchase in purchases:
        items = [item for item in purchase_items if item["PurchaseID"] == purchase["PurchaseID"]]
        for item in items:
            medicine = db.get_medicine({"MedicineID": item["MedicineID"]})
            
            purchase_history.append({
                "date": purchase["DateOfPurchase"],
                "medicine": medicine[0]["Name"] if medicine else "Unknown",
                "quantity": item["Quantity"],
                "total": item["Quantity"] * medicine[0]["Price"] if medicine else 0
            })
    
    return templates.TemplateResponse("customer_history.html", {
        "request": request,
        "customer": customer[0],
        "purchase_history": purchase_history,
        "store_id": store_id
    }) 