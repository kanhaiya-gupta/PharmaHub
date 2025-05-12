from .database_sqlite import SQLiteDatabase
from datetime import datetime
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
                db.insert_store(store)
                logger.info(f"Added store: {store['StoreName']}")
            except Exception as e:
                logger.error(f"Failed to add store {store['StoreName']}: {e}")
                continue
        
        return True
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        return False

if __name__ == "__main__":
    init_database() 