from fastapi import APIRouter, Request, Form, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.database.database_sqlite import SQLiteDatabase
from datetime import datetime, timedelta
from typing import Optional, List

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Dependency to get database instance
def get_db():
    return SQLiteDatabase('medical_store.db')

def get_dashboard_stats(db: SQLiteDatabase):
    """Get real-time statistics for the dashboard."""
    try:
        # Get total medicines
        medicines = db.get_medicine()
        total_medicines = len(medicines)
        
        # Get low stock medicines (less than 10 units)
        low_stock = len([m for m in medicines if m['StockQuantity'] < 10])
        
        # Get medicines expiring in next 30 days
        today = datetime.now()
        thirty_days_later = today + timedelta(days=30)
        expiring_soon = len([
            m for m in medicines 
            if m['ExpiryDate'] and datetime.strptime(m['ExpiryDate'], '%Y-%m-%d') <= thirty_days_later
        ])
        
        return {
            'total_medicines': total_medicines,
            'low_stock': low_stock,
            'expiring_soon': expiring_soon
        }
    except Exception as e:
        print(f"Error getting dashboard stats: {e}")
        return {
            'total_medicines': 0,
            'low_stock': 0,
            'expiring_soon': 0
        }

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: SQLiteDatabase = Depends(get_db)):
    stats = get_dashboard_stats(db)
    stores = db.get_store()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "stats": stats,
        "stores": stores
    })

@router.get("/medicines", response_class=HTMLResponse)
async def get_medicines(request: Request, db: SQLiteDatabase = Depends(get_db)):
    medicines = db.get_medicine()
    return templates.TemplateResponse("medicines.html", {
        "request": request,
        "medicines": medicines
    })

@router.get("/customers", response_class=HTMLResponse)
async def get_customers(request: Request, db: SQLiteDatabase = Depends(get_db)):
    customers = db.get_customer()
    return templates.TemplateResponse("customers.html", {
        "request": request,
        "customers": customers
    })

@router.get("/operators", response_class=HTMLResponse)
async def get_operators(request: Request, db: SQLiteDatabase = Depends(get_db)):
    operators = db.get_operator()
    return templates.TemplateResponse("operators.html", {
        "request": request,
        "operators": operators
    })

@router.get("/purchases", response_class=HTMLResponse)
async def get_purchases(request: Request, db: SQLiteDatabase = Depends(get_db)):
    purchases = db.get_purchase()
    purchase_items = db.get_purchase_item()
    
    # Combine purchase data with related information
    purchase_details = []
    for purchase in purchases:
        # Get customer name
        customer = db.get_customer({"CustomerID": purchase["CustomerID"]})
        customer_name = customer[0]["Name"] if customer else "Unknown"
        
        # Get operator name
        operator = db.get_operator({"OperatorID": purchase["OperatorID"]})
        operator_name = operator[0]["Name"] if operator else "Unknown"
        
        # Get medicine details from purchase items
        items = [item for item in purchase_items if item["PurchaseID"] == purchase["PurchaseID"]]
        for item in items:
            medicine = db.get_medicine({"MedicineID": item["MedicineID"]})
            medicine_name = medicine[0]["Name"] if medicine else "Unknown"
            
            purchase_details.append({
                "customer": customer_name,
                "medicine": medicine_name,
                "quantity": item["Quantity"],
                "operator": operator_name,
                "date": purchase["DateOfPurchase"]
            })
    
    return templates.TemplateResponse("purchases.html", {
        "request": request,
        "purchases": purchase_details
    })

# Medicine Routes
@router.post("/medicines/add")
async def add_medicine(
    name: str = Form(...),
    brand: str = Form(...),
    batch_number: str = Form(...),
    expiry_date: str = Form(...),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    type: str = Form(...),
    requires_prescription: str = Form(...),
    schedule_category: str = Form(...),
    storage_location: str = Form(...),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        # First, get or create storage location
        storage_data = {"Label": storage_location}
        storage_id = db.insert_storage_location(storage_data)
        
        # Prepare medicine data
        medicine_data = {
            "Name": name,
            "Brand": brand,
            "BatchNumber": batch_number,
            "ExpiryDate": expiry_date,
            "Price": price,
            "StockQuantity": stock_quantity,
            "Type": type,
            "RequiresPrescription": requires_prescription == "Yes",
            "ScheduleCategory": schedule_category,
            "DateAdded": datetime.now().strftime("%Y-%m-%d"),
            "StorageLocationID": storage_id
        }
        
        # Insert medicine
        medicine_id = db.insert_medicine(medicine_data)
        if medicine_id:
            return RedirectResponse(url="/medicines", status_code=303)
        else:
            raise HTTPException(status_code=400, detail="Failed to add medicine")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/medicines/batch-add")
async def add_batch_medicines(
    invoice_number: str = Form(...),
    supplier: str = Form(...),
    batch_number: str = Form(...),
    batch_size: int = Form(...),
    expiry_date: str = Form(...),
    storage_location: str = Form(...),
    items: List[dict] = Form(...),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        # Add batch record
        batch_id = db.add_batch(
            invoice_number=invoice_number,
            supplier=supplier,
            batch_number=batch_number,
            batch_size=batch_size,
            expiry_date=datetime.strptime(expiry_date, "%Y-%m-%d"),
            storage_location=storage_location
        )

        # Add each medicine in the batch
        for item in items:
            db.add_medicine(
                name=item['name'],
                brand=item['brand'],
                batch_number=batch_number,
                expiry_date=datetime.strptime(expiry_date, "%Y-%m-%d"),
                storage_location=storage_location,
                type=item.get('type', ''),
                price=float(item['price']),
                stock_quantity=int(item['quantity']),
                schedule_category=item.get('schedule_category', ''),
                requires_prescription=item['requires_prescription'] == 'Yes',
                barcode=item.get('barcode')
            )

        return RedirectResponse(url="/medicines", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/medicines/barcode/{barcode}")
async def get_medicine_by_barcode(barcode: str, db: SQLiteDatabase = Depends(get_db)):
    medicine = db.get_medicine_by_barcode(barcode)
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return medicine

@router.get("/api/medicines/batch/{barcode}")
async def get_batch_by_barcode(barcode: str, db: SQLiteDatabase = Depends(get_db)):
    batch = db.get_batch_by_barcode(barcode)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch

# Customer Routes
@router.post("/customers/add")
async def add_customer(
    name: str = Form(...),
    contact: str = Form(...),
    address: str = Form(...),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        customer_data = {
            "Name": name,
            "ContactInfo": contact,
            "Address": address
        }
        customer_id = db.insert_customer(customer_data)
        if customer_id:
            return RedirectResponse(url="/customers", status_code=303)
        else:
            raise HTTPException(status_code=400, detail="Failed to add customer")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Operator Routes
@router.post("/operators/add")
async def add_operator(
    name: str = Form(...),
    role: str = Form(...),
    contact: str = Form(...),
    email: str = Form(...),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        operator_data = {
            "Name": name,
            "Role": role,
            "ContactInfo": contact,
            "Email": email
        }
        operator_id = db.insert_operator(operator_data)
        if operator_id:
            return RedirectResponse(url="/operators", status_code=303)
        else:
            raise HTTPException(status_code=400, detail="Failed to add operator")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Purchase Routes
@router.post("/purchases/add")
async def add_purchase(
    customer_name: str = Form(...),
    operator_name: str = Form(...),
    medicine_name: str = Form(...),
    quantity: int = Form(...),
    purchase_date: str = Form(...),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        # Get customer and operator IDs
        customers = db.get_customer({"Name": customer_name})
        operators = db.get_operator({"Name": operator_name})
        medicines = db.get_medicine({"Name": medicine_name})
        
        if not customers or not operators or not medicines:
            raise HTTPException(status_code=400, detail="Customer, operator, or medicine not found")
        
        customer_id = customers[0]["CustomerID"]
        operator_id = operators[0]["OperatorID"]
        medicine_id = medicines[0]["MedicineID"]
        price_per_unit = medicines[0]["Price"]
        
        # Create purchase record
        purchase_data = {
            "CustomerID": customer_id,
            "OperatorID": operator_id,
            "DateOfPurchase": purchase_date,
            "TotalAmount": price_per_unit * quantity
        }
        purchase_id = db.insert_purchase(purchase_data)
        
        if purchase_id:
            # Create purchase item record
            purchase_item_data = {
                "PurchaseID": purchase_id,
                "MedicineID": medicine_id,
                "Quantity": quantity,
                "PricePerUnit": price_per_unit
            }
            db.insert_purchase_item(purchase_item_data)
            
            # Update medicine stock
            new_quantity = medicines[0]["StockQuantity"] - quantity
            db.update_medicine({"MedicineID": medicine_id}, {"StockQuantity": new_quantity})
            
            return RedirectResponse(url="/purchases", status_code=303)
        else:
            raise HTTPException(status_code=400, detail="Failed to record purchase")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Store Management Routes
@router.get("/stores", response_class=HTMLResponse)
async def list_stores(request: Request, db: SQLiteDatabase = Depends(get_db)):
    stores = db.get_store()
    return templates.TemplateResponse("stores.html", {
        "request": request,
        "stores": stores
    })

@router.post("/stores/add")
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

@router.get("/stores/{store_id}", response_class=HTMLResponse)
async def get_store_dashboard(
    request: Request,
    store_id: int,
    db: SQLiteDatabase = Depends(get_db)
):
    store = db.get_store({"StoreID": store_id})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    store = store[0]
    stats = get_dashboard_stats(db)
    
    return templates.TemplateResponse("store_dashboard.html", {
        "request": request,
        "store": store,
        "stats": stats
    })

# Store-specific routes
@router.get("/stores/{store_id}/medicines", response_class=HTMLResponse)
async def get_store_medicines(
    request: Request,
    store_id: int,
    db: SQLiteDatabase = Depends(get_db)
):
    medicines = db.get_medicine(store_id=store_id)
    return templates.TemplateResponse("medicines.html", {
        "request": request,
        "medicines": medicines,
        "store_id": store_id
    })

@router.get("/stores/{store_id}/customers", response_class=HTMLResponse)
async def get_store_customers(
    request: Request,
    store_id: int,
    db: SQLiteDatabase = Depends(get_db)
):
    customers = db.get_customer({"StoreID": store_id})
    return templates.TemplateResponse("customers.html", {
        "request": request,
        "customers": customers,
        "store_id": store_id
    })

@router.get("/stores/{store_id}/operators", response_class=HTMLResponse)
async def get_store_operators(
    request: Request,
    store_id: int,
    db: SQLiteDatabase = Depends(get_db)
):
    operators = db.get_operator({"StoreID": store_id})
    return templates.TemplateResponse("operators.html", {
        "request": request,
        "operators": operators,
        "store_id": store_id
    })

@router.get("/stores/{store_id}/purchases", response_class=HTMLResponse)
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
        # Get customer name
        customer = db.get_customer({"CustomerID": purchase["CustomerID"]})
        customer_name = customer[0]["Name"] if customer else "Unknown"
        
        # Get operator name
        operator = db.get_operator({"OperatorID": purchase["OperatorID"]})
        operator_name = operator[0]["Name"] if operator else "Unknown"
        
        # Get medicine details from purchase items
        items = [item for item in purchase_items if item["PurchaseID"] == purchase["PurchaseID"]]
        for item in items:
            medicine = db.get_medicine(store_id=store_id, condition={"MedicineID": item["MedicineID"]})
            medicine_name = medicine[0]["Name"] if medicine else "Unknown"
            
            purchase_details.append({
                "customer": customer_name,
                "medicine": medicine_name,
                "quantity": item["Quantity"],
                "operator": operator_name,
                "date": purchase["DateOfPurchase"]
            })
    
    return templates.TemplateResponse("purchases.html", {
        "request": request,
        "purchases": purchase_details,
        "store_id": store_id
    })

# Update existing routes to include store_id
@router.post("/stores/{store_id}/medicines/add")
async def add_medicine(
    store_id: int,
    name: str = Form(...),
    brand: str = Form(...),
    batch_number: str = Form(...),
    expiry_date: str = Form(...),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    type: str = Form(...),
    requires_prescription: str = Form(...),
    schedule_category: str = Form(...),
    storage_location: str = Form(...),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        # First, get or create storage location
        storage_data = {
            "StoreID": store_id,
            "Label": storage_location
        }
        storage_id = db.insert_storage_location(storage_data)
        
        # Prepare medicine data
        medicine_data = {
            "StoreID": store_id,
            "Name": name,
            "Brand": brand,
            "BatchNumber": batch_number,
            "ExpiryDate": expiry_date,
            "Price": price,
            "StockQuantity": stock_quantity,
            "Type": type,
            "RequiresPrescription": requires_prescription == "Yes",
            "ScheduleCategory": schedule_category,
            "DateAdded": datetime.now().strftime("%Y-%m-%d"),
            "StorageLocationID": storage_id
        }
        
        # Insert medicine
        medicine_id = db.insert_medicine(medicine_data)
        if medicine_id:
            return RedirectResponse(url=f"/stores/{store_id}/medicines", status_code=303)
        else:
            raise HTTPException(status_code=400, detail="Failed to add medicine")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Similar updates for other routes...

# Data Manager Routes (Access to all stores)
@router.get("/data-manager/dashboard", response_class=HTMLResponse)
async def data_manager_dashboard(request: Request, db: SQLiteDatabase = Depends(get_db)):
    stores = db.get_store()
    all_stats = {}
    
    for store in stores:
        all_stats[store["StoreID"]] = get_dashboard_stats(db)
    
    return templates.TemplateResponse("data_manager_dashboard.html", {
        "request": request,
        "stores": stores,
        "all_stats": all_stats
    })

@router.get("/data-manager/stores/{store_id}/inventory", response_class=HTMLResponse)
async def view_store_inventory(
    request: Request,
    store_id: int,
    db: SQLiteDatabase = Depends(get_db)
):
    store = db.get_store({"StoreID": store_id})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    medicines = db.get_medicine(store_id=store_id)
    return templates.TemplateResponse("store_inventory.html", {
        "request": request,
        "store": store[0],
        "medicines": medicines
    })

@router.get("/data-manager/stores/{store_id}/sales", response_class=HTMLResponse)
async def view_store_sales(
    request: Request,
    store_id: int,
    db: SQLiteDatabase = Depends(get_db)
):
    store = db.get_store({"StoreID": store_id})
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    purchases = db.get_purchase({"StoreID": store_id})
    return templates.TemplateResponse("store_sales.html", {
        "request": request,
        "store": store[0],
        "purchases": purchases
    }) 