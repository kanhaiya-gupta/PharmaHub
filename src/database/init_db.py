from .database_sqlite import SQLiteDatabase
from datetime import datetime, timedelta
import os
from ..utils.loggers import LoggerFactory

# Set up logger
base_dir = os.path.abspath(os.path.dirname(__file__))
log_dir = os.path.join(base_dir, "..", "..", "results", "logs")
logger = LoggerFactory("InitDBLogger", log_dir, "init_db").get_logger()

def init_database():
    """Initialize the database with required data."""
    try:
        # Initialize database
        db = SQLiteDatabase('medical_store.db')
        
        # Add medical stores
        stores = [
            {
                "StoreName": "Michael Medical Store",
                "Address": "123 Main Street, City Center",
                "ContactNumber": "+1-555-0123",
                "LicenseNumber": "MS001",
                "OpeningDate": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "StoreName": "Jackson Medical Store",
                "Address": "456 Oak Avenue, Downtown",
                "ContactNumber": "+1-555-0124",
                "LicenseNumber": "MS002",
                "OpeningDate": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "StoreName": "Bob Medical Store",
                "Address": "789 Pine Road, Uptown",
                "ContactNumber": "+1-555-0125",
                "LicenseNumber": "MS003",
                "OpeningDate": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "StoreName": "Gill Medical Store",
                "Address": "321 Elm Street, Westside",
                "ContactNumber": "+1-555-0126",
                "LicenseNumber": "MS004",
                "OpeningDate": datetime.now().strftime("%Y-%m-%d")
            }
        ]
        
        for store in stores:
            try:
                store_id = db.insert_store(store)
                logger.info(f"Added store: {store['StoreName']} with ID: {store_id}")
                
                # Add operators for each store
                operators = [
                    {
                        "StoreID": store_id,
                        "Name": f"Manager {store['StoreName']}",
                        "Email": f"manager@{store['StoreName'].lower().replace(' ', '')}.com",
                        "Role": "Manager",
                        "IsAdmin": True
                    },
                    {
                        "StoreID": store_id,
                        "Name": f"Pharmacist {store['StoreName']}",
                        "Email": f"pharmacist@{store['StoreName'].lower().replace(' ', '')}.com",
                        "Role": "Pharmacist",
                        "IsAdmin": False
                    },
                    {
                        "StoreID": store_id,
                        "Name": f"Cashier {store['StoreName']}",
                        "Email": f"cashier@{store['StoreName'].lower().replace(' ', '')}.com",
                        "Role": "Cashier",
                        "IsAdmin": False
                    }
                ]
                
                for operator in operators:
                    operator_id = db.insert_operator(operator)
                    logger.info(f"Added operator: {operator['Name']} with ID: {operator_id}")
                
                # Add storage locations
                locations = [
                    {
                        "StoreID": store_id,
                        "Label": "Main Shelf",
                        "IsTemperatureControlled": False,
                        "Notes": "Regular storage area"
                    },
                    {
                        "StoreID": store_id,
                        "Label": "Refrigerated Area",
                        "IsTemperatureControlled": True,
                        "Notes": "For temperature-sensitive medicines"
                    }
                ]
                
                for location in locations:
                    location_id = db.insert_storage_location(location)
                    logger.info(f"Added storage location: {location['Label']} with ID: {location_id}")
                
                # Add sample medicines
                medicines = [
                    {
                        "StoreID": store_id,
                        "Name": "Paracetamol 500mg",
                        "Brand": "Generic",
                        "Price": 5.99,
                        "StockQuantity": 100,
                        "Type": "Pain Relief",
                        "RequiresPrescription": False,
                        "ScheduleCategory": "OTC",
                        "DateAdded": datetime.now().strftime("%Y-%m-%d"),
                        "StorageLocationID": 1
                    },
                    {
                        "StoreID": store_id,
                        "Name": "Amoxicillin 250mg",
                        "Brand": "Generic",
                        "Price": 15.99,
                        "StockQuantity": 50,
                        "Type": "Antibiotic",
                        "RequiresPrescription": True,
                        "ScheduleCategory": "Prescription",
                        "DateAdded": datetime.now().strftime("%Y-%m-%d"),
                        "StorageLocationID": 1
                    },
                    {
                        "StoreID": store_id,
                        "Name": "Insulin Regular",
                        "Brand": "Novo Nordisk",
                        "Price": 45.99,
                        "StockQuantity": 25,
                        "Type": "Diabetes",
                        "RequiresPrescription": True,
                        "ScheduleCategory": "Prescription",
                        "DateAdded": datetime.now().strftime("%Y-%m-%d"),
                        "StorageLocationID": 2
                    }
                ]
                
                for medicine in medicines:
                    medicine_id = db.insert_medicine(medicine)
                    logger.info(f"Added medicine: {medicine['Name']} with ID: {medicine_id}")
                
                # Add sample customers
                customers = [
                    {
                        "StoreID": store_id,
                        "Name": "John Doe",
                        "ContactInfo": "+1-555-0001",
                        "Age": 35,
                        "Gender": "Male",
                        "Address": "123 Customer Street"
                    },
                    {
                        "StoreID": store_id,
                        "Name": "Jane Smith",
                        "ContactInfo": "+1-555-0002",
                        "Age": 28,
                        "Gender": "Female",
                        "Address": "456 Customer Avenue"
                    }
                ]
                
                for customer in customers:
                    customer_id = db.insert_customer(customer)
                    logger.info(f"Added customer: {customer['Name']} with ID: {customer_id}")
                
            except Exception as e:
                logger.error(f"Failed to add data for store {store['StoreName']}: {e}")
                continue
        
        return True
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        return False

if __name__ == "__main__":
    init_database() 