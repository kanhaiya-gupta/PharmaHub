from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.database.database_sqlite import SQLiteDatabase

router = APIRouter(prefix="/operators", tags=["operators"])
templates = Jinja2Templates(directory="templates")

# Dependency to get database instance
def get_db():
    return SQLiteDatabase('medical_store.db')

@router.get("/", response_class=HTMLResponse)
async def list_operators(
    request: Request,
    store_id: int = None,
    db: SQLiteDatabase = Depends(get_db)
):
    filter_dict = {"StoreID": store_id} if store_id else {}
    operators = db.get_operator(filter_dict)
    return templates.TemplateResponse("operators.html", {
        "request": request,
        "operators": operators,
        "store_id": store_id
    })

@router.post("/add")
async def add_operator(
    name: str = Form(...),
    contact_number: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    store_id: int = Form(...),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        operator_data = {
            "Name": name,
            "ContactNumber": contact_number,
            "Email": email,
            "Role": role,
            "StoreID": store_id
        }
        
        operator_id = db.insert_operator(operator_data)
        if operator_id:
            return RedirectResponse(url=f"/operators?store_id={store_id}", status_code=303)
        else:
            raise HTTPException(status_code=400, detail="Failed to add operator")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{operator_id}/update")
async def update_operator(
    operator_id: int,
    name: str = Form(...),
    contact_number: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    store_id: int = Form(...),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        operator_data = {
            "Name": name,
            "ContactNumber": contact_number,
            "Email": email,
            "Role": role
        }
        
        success = db.update_operator(operator_id, operator_data)
        if success:
            return RedirectResponse(url=f"/operators?store_id={store_id}", status_code=303)
        else:
            raise HTTPException(status_code=400, detail="Failed to update operator")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{operator_id}/delete")
async def delete_operator(
    operator_id: int,
    store_id: int = Form(...),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        success = db.delete_operator(operator_id)
        if success:
            return RedirectResponse(url=f"/operators?store_id={store_id}", status_code=303)
        else:
            raise HTTPException(status_code=400, detail="Failed to delete operator")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{operator_id}/activity", response_class=HTMLResponse)
async def get_operator_activity(
    request: Request,
    operator_id: int,
    store_id: int = None,
    db: SQLiteDatabase = Depends(get_db)
):
    # Get operator details
    operator = db.get_operator({"OperatorID": operator_id})
    if not operator:
        raise HTTPException(status_code=404, detail="Operator not found")
    
    # Get purchase history
    purchases = db.get_purchase({"OperatorID": operator_id})
    purchase_items = db.get_purchase_item()
    
    # Combine purchase data with customer and medicine information
    activity_history = []
    for purchase in purchases:
        customer = db.get_customer({"CustomerID": purchase["CustomerID"]})
        items = [item for item in purchase_items if item["PurchaseID"] == purchase["PurchaseID"]]
        
        for item in items:
            medicine = db.get_medicine({"MedicineID": item["MedicineID"]})
            
            activity_history.append({
                "date": purchase["DateOfPurchase"],
                "customer": customer[0]["Name"] if customer else "Unknown",
                "medicine": medicine[0]["Name"] if medicine else "Unknown",
                "quantity": item["Quantity"],
                "total": item["Quantity"] * medicine[0]["Price"] if medicine else 0
            })
    
    return templates.TemplateResponse("operator_activity.html", {
        "request": request,
        "operator": operator[0],
        "activity_history": activity_history,
        "store_id": store_id
    }) 