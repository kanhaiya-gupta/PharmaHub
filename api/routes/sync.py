from fastapi import APIRouter, Request, Form, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.database.database_sqlite import SQLiteDatabase
from src.utils.loggers import LoggerFactory
import jwt
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

router = APIRouter(prefix="/sync", tags=["sync"])
templates = Jinja2Templates(directory="templates")

# Set up logger
base_dir = os.path.abspath(os.path.dirname(__file__))
log_dir = os.path.join(base_dir, "..", "..", "results", "logs")
logger = LoggerFactory("SyncLogger", log_dir, "sync_api").get_logger()

# JWT configuration
SECRET_KEY = "your-secret-key"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Dependency to get database instance
def get_db():
    return SQLiteDatabase('medical_store.db')

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verify_token(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

@router.post("/connect")
async def connect_store(
    store_id: int = Form(...),
    store_name: str = Form(...),
    license_number: str = Form(...),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        # Verify store credentials
        store = db.get_store({
            "StoreID": store_id,
            "StoreName": store_name,
            "LicenseNumber": license_number
        })
        
        if not store:
            raise HTTPException(status_code=401, detail="Invalid store credentials")
        
        # Generate access token
        token_data = {
            "store_id": store_id,
            "store_name": store_name,
            "license_number": license_number
        }
        access_token = create_access_token(token_data)
        
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Error connecting store: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/changes")
async def get_changes(
    last_sync: str = None,
    token: dict = Depends(verify_token),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        store_id = token["store_id"]
        changes = {
            "medicines": [],
            "customers": [],
            "operators": [],
            "purchases": []
        }
        
        # Get changes since last sync
        if last_sync:
            last_sync_date = datetime.strptime(last_sync, "%Y-%m-%d %H:%M:%S")
            
            # Get medicine changes
            medicines = db.get_medicine({"StoreID": store_id})
            for medicine in medicines:
                if datetime.strptime(medicine["LastModified"], "%Y-%m-%d %H:%M:%S") > last_sync_date:
                    changes["medicines"].append(medicine)
            
            # Get customer changes
            customers = db.get_customer({"StoreID": store_id})
            for customer in customers:
                if datetime.strptime(customer["LastModified"], "%Y-%m-%d %H:%M:%S") > last_sync_date:
                    changes["customers"].append(customer)
            
            # Get operator changes
            operators = db.get_operator({"StoreID": store_id})
            for operator in operators:
                if datetime.strptime(operator["LastModified"], "%Y-%m-%d %H:%M:%S") > last_sync_date:
                    changes["operators"].append(operator)
            
            # Get purchase changes
            purchases = db.get_purchase({"StoreID": store_id})
            for purchase in purchases:
                if datetime.strptime(purchase["DateOfPurchase"], "%Y-%m-%d %H:%M:%S") > last_sync_date:
                    changes["purchases"].append(purchase)
        
        return changes
    except Exception as e:
        logger.error(f"Error getting changes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/push")
async def push_changes(
    changes: dict,
    token: dict = Depends(verify_token),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        store_id = token["store_id"]
        
        # Process medicine changes
        for medicine in changes.get("medicines", []):
            if "MedicineID" in medicine:
                db.update_medicine(medicine["MedicineID"], medicine)
            else:
                medicine["StoreID"] = store_id
                db.insert_medicine(medicine)
        
        # Process customer changes
        for customer in changes.get("customers", []):
            if "CustomerID" in customer:
                db.update_customer(customer["CustomerID"], customer)
            else:
                customer["StoreID"] = store_id
                db.insert_customer(customer)
        
        # Process operator changes
        for operator in changes.get("operators", []):
            if "OperatorID" in operator:
                db.update_operator(operator["OperatorID"], operator)
            else:
                operator["StoreID"] = store_id
                db.insert_operator(operator)
        
        # Process purchase changes
        for purchase in changes.get("purchases", []):
            if "PurchaseID" in purchase:
                db.update_purchase(purchase["PurchaseID"], purchase)
            else:
                purchase["StoreID"] = store_id
                db.insert_purchase(purchase)
        
        return {"status": "success", "message": "Changes synchronized successfully"}
    except Exception as e:
        logger.error(f"Error pushing changes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_sync_status(
    token: dict = Depends(verify_token),
    db: SQLiteDatabase = Depends(get_db)
):
    try:
        store_id = token["store_id"]
        store = db.get_store({"StoreID": store_id})
        
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Get last sync time
        last_sync = store[0].get("LastSyncTime", "Never")
        
        # Get sync statistics
        medicines = db.get_medicine({"StoreID": store_id})
        customers = db.get_customer({"StoreID": store_id})
        operators = db.get_operator({"StoreID": store_id})
        purchases = db.get_purchase({"StoreID": store_id})
        
        return {
            "store_id": store_id,
            "store_name": store[0]["StoreName"],
            "last_sync": last_sync,
            "statistics": {
                "total_medicines": len(medicines),
                "total_customers": len(customers),
                "total_operators": len(operators),
                "total_purchases": len(purchases)
            }
        }
    except Exception as e:
        logger.error(f"Error getting sync status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 