from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.database.database_sqlite import SQLiteDatabase
from datetime import datetime

router = APIRouter(prefix="/purchases", tags=["purchases"])
templates = Jinja2Templates(directory="templates")

# Dependency to get database instance
def get_db():
    return SQLiteDatabase('medical_store.db')

@router.get("/", response_class=HTMLResponse)
async def list_purchases(
    request: Request,
    store_id: int = None,
    db: SQLiteDatabase = Depends(get_db)
):
    filter_dict = {"StoreID": store_id} if store_id else {}
    purchases = db.get_purchase(filter_dict)
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
                "purchase_id": purchase["PurchaseID"],
                "date": purchase["DateOfPurchase"],
                "customer": customer[0]["Name"] if customer else "Unknown",
                "medicine": medicine[0]["Name"] if medicine else "Unknown",
                "quantity": item["Quantity"],
                "operator": operator[0]["Name"] if operator else "Unknown",
                "total": item["Quantity"] * medicine[0]["Price"] if medicine else 0
            })
    
    return templates.TemplateResponse("purchases.html", {
        "request": request,
        "purchases": purchase_details,
        "store_id": store_id
    })

@router.post("/add")
async def add_purchase(
    customer_id: int = Form(...),
    operator_id: int = Form(...),
    store_id: int = Form(...),
    items: str = Form(...),  # JSON string of items
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        import json
        items_list = json.loads(items)
        
        # Create purchase record
        purchase_data = {
            "CustomerID": customer_id,
            "OperatorID": operator_id,
            "StoreID": store_id,
            "DateOfPurchase": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        purchase_id = db.insert_purchase(purchase_data)
        if not purchase_id:
            raise HTTPException(status_code=400, detail="Failed to create purchase")
        
        # Add purchase items and update stock
        total_amount = 0
        for item in items_list:
            medicine = db.get_medicine({"MedicineID": item["medicine_id"]})
            if not medicine:
                raise HTTPException(status_code=404, detail=f"Medicine {item['medicine_id']} not found")
            
            medicine = medicine[0]
            if medicine["StockQuantity"] < item["quantity"]:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for {medicine['Name']}")
            
            # Add purchase item
            item_data = {
                "PurchaseID": purchase_id,
                "MedicineID": item["medicine_id"],
                "Quantity": item["quantity"]
            }
            db.insert_purchase_item(item_data)
            
            # Update stock
            new_quantity = medicine["StockQuantity"] - item["quantity"]
            db.update_medicine(item["medicine_id"], {"StockQuantity": new_quantity})
            
            total_amount += item["quantity"] * medicine["Price"]
        
        return RedirectResponse(url=f"/purchases?store_id={store_id}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{purchase_id}", response_class=HTMLResponse)
async def get_purchase_details(
    request: Request,
    purchase_id: int,
    store_id: int = None,
    db: SQLiteDatabase = Depends(get_db)
):
    purchase = db.get_purchase({"PurchaseID": purchase_id})
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    
    purchase = purchase[0]
    customer = db.get_customer({"CustomerID": purchase["CustomerID"]})
    operator = db.get_operator({"OperatorID": purchase["OperatorID"]})
    
    purchase_items = db.get_purchase_item({"PurchaseID": purchase_id})
    items_details = []
    total_amount = 0
    
    for item in purchase_items:
        medicine = db.get_medicine({"MedicineID": item["MedicineID"]})
        if medicine:
            medicine = medicine[0]
            item_total = item["Quantity"] * medicine["Price"]
            total_amount += item_total
            
            items_details.append({
                "medicine": medicine["Name"],
                "quantity": item["Quantity"],
                "price": medicine["Price"],
                "total": item_total
            })
    
    return templates.TemplateResponse("purchase_details.html", {
        "request": request,
        "purchase": purchase,
        "customer": customer[0] if customer else None,
        "operator": operator[0] if operator else None,
        "items": items_details,
        "total_amount": total_amount,
        "store_id": store_id
    })

@router.get("/daily-report", response_class=HTMLResponse)
async def get_daily_report(
    request: Request,
    store_id: int = None,
    date: str = None,
    db: SQLiteDatabase = Depends(get_db)
):
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    filter_dict = {"StoreID": store_id} if store_id else {}
    purchases = db.get_purchase(filter_dict)
    purchase_items = db.get_purchase_item()
    
    # Filter purchases for the specified date
    daily_purchases = []
    total_sales = 0
    medicine_sales = {}
    
    for purchase in purchases:
        if purchase["DateOfPurchase"].startswith(date):
            items = [item for item in purchase_items if item["PurchaseID"] == purchase["PurchaseID"]]
            
            for item in items:
                medicine = db.get_medicine({"MedicineID": item["MedicineID"]})
                if medicine:
                    medicine = medicine[0]
                    item_total = item["Quantity"] * medicine["Price"]
                    total_sales += item_total
                    
                    # Track medicine sales
                    if medicine["Name"] not in medicine_sales:
                        medicine_sales[medicine["Name"]] = {
                            "quantity": 0,
                            "total": 0
                        }
                    medicine_sales[medicine["Name"]]["quantity"] += item["Quantity"]
                    medicine_sales[medicine["Name"]]["total"] += item_total
                    
                    daily_purchases.append({
                        "time": purchase["DateOfPurchase"].split()[1],
                        "medicine": medicine["Name"],
                        "quantity": item["Quantity"],
                        "total": item_total
                    })
    
    return templates.TemplateResponse("daily_report.html", {
        "request": request,
        "date": date,
        "purchases": daily_purchases,
        "total_sales": total_sales,
        "medicine_sales": medicine_sales,
        "store_id": store_id
    }) 