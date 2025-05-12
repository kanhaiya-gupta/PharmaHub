import sqlite3
import os
from typing import Dict, List, Any, Optional
from src.utils.loggers import LoggerFactory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime


class SQLiteDatabase:
    """Manages SQLite database for medical store operations."""

    def __init__(self, db_name: str, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the database with a new schema.

        Args:
            db_name: Name of the SQLite database file (e.g., 'medical_store.db').
            config: Optional configuration dictionary for future extensions.
        """
        # Set up base directories
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.results_dir = os.path.join(base_dir, "results")
        self.db_path = os.path.join(self.results_dir, db_name)
        
        # Create results directory if it doesn't exist
        os.makedirs(self.results_dir, exist_ok=True)
        
        self.config = config or {}

        # Set up logger
        log_dir = os.path.join(self.results_dir, "logs")
        logger_name = "DatabaseLogger"
        log_file_base = "database"
        self.logger = LoggerFactory(logger_name, log_dir, log_file_base).get_logger()
        self.logger.info("Initializing Database Processor")

        # Create schema
        self._create_schema()

        # Set up SQLAlchemy
        SQLALCHEMY_DATABASE_URL = f"sqlite:///{self.db_path}"
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def _create_schema(self) -> None:
        """Create the database schema if it doesn't exist."""
        self.logger.info("Creating database schema")
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create MedicalStore table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS MedicalStore (
                    StoreID INTEGER PRIMARY KEY AUTOINCREMENT,
                    StoreName TEXT NOT NULL,
                    Address TEXT NOT NULL,
                    ContactNumber TEXT,
                    LicenseNumber TEXT NOT NULL,
                    OpeningDate TEXT
                )
            ''')

            # Create Operator table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Operator (
                    OperatorID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL,
                    ContactInfo TEXT,
                    Role TEXT,
                    Email TEXT,
                    AssignedStoreID INTEGER,
                    FOREIGN KEY (AssignedStoreID) REFERENCES MedicalStore(StoreID)
                )
            ''')

            # Create Customer table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Customer (
                    CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL,
                    ContactInfo TEXT,
                    Age INTEGER,
                    Gender TEXT,
                    Address TEXT
                )
            ''')

            # Create StorageLocation table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS StorageLocation (
                    StorageLocationID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Label TEXT NOT NULL,
                    IsTemperatureControlled BOOLEAN,
                    Notes TEXT
                )
            ''')

            # Create Batch table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Batch (
                    BatchID INTEGER PRIMARY KEY AUTOINCREMENT,
                    InvoiceNumber TEXT NOT NULL,
                    Supplier TEXT NOT NULL,
                    BatchNumber TEXT NOT NULL,
                    BatchSize INTEGER NOT NULL,
                    ExpiryDate DATE NOT NULL,
                    StorageLocation TEXT NOT NULL,
                    DateReceived DATE DEFAULT CURRENT_TIMESTAMP,
                    Barcode TEXT UNIQUE
                )
            ''')

            # Create BatchItem table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS BatchItem (
                    BatchItemID INTEGER PRIMARY KEY AUTOINCREMENT,
                    BatchID INTEGER NOT NULL,
                    MedicineID INTEGER NOT NULL,
                    Quantity INTEGER NOT NULL,
                    FOREIGN KEY (BatchID) REFERENCES Batch(BatchID),
                    FOREIGN KEY (MedicineID) REFERENCES Medicine(MedicineID)
                )
            ''')

            # Create Medicine table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Medicine (
                    MedicineID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL,
                    Brand TEXT,
                    BatchNumber TEXT,
                    ExpiryDate DATE,
                    Price REAL NOT NULL,
                    StockQuantity INTEGER NOT NULL,
                    Type TEXT,
                    RequiresPrescription BOOLEAN,
                    ScheduleCategory TEXT,
                    DateAdded TEXT,
                    StorageLocationID INTEGER,
                    Barcode TEXT UNIQUE,
                    FOREIGN KEY (StorageLocationID) REFERENCES StorageLocation(StorageLocationID)
                )
            ''')

            # Create Purchase table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Purchase (
                    PurchaseID INTEGER PRIMARY KEY AUTOINCREMENT,
                    CustomerID INTEGER,
                    OperatorID INTEGER,
                    DateOfPurchase DATE,
                    TotalAmount REAL NOT NULL,
                    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
                    FOREIGN KEY (OperatorID) REFERENCES Operator(OperatorID)
                )
            ''')

            # Create PurchaseItem table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS PurchaseItem (
                    PurchaseItemID INTEGER PRIMARY KEY AUTOINCREMENT,
                    PurchaseID INTEGER,
                    MedicineID INTEGER,
                    Quantity INTEGER NOT NULL,
                    PricePerUnit REAL NOT NULL,
                    FOREIGN KEY (PurchaseID) REFERENCES Purchase(PurchaseID),
                    FOREIGN KEY (MedicineID) REFERENCES Medicine(MedicineID)
                )
            ''')

            # Create Prescription table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Prescription (
                    PrescriptionID INTEGER PRIMARY KEY AUTOINCREMENT,
                    CustomerID INTEGER,
                    DoctorName TEXT,
                    IssueDate DATE,
                    ExpiryDate DATE,
                    Status TEXT,
                    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
                )
            ''')

            # Create Insurance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Insurance (
                    InsuranceID INTEGER PRIMARY KEY AUTOINCREMENT,
                    CustomerID INTEGER,
                    Provider TEXT,
                    PolicyNumber TEXT,
                    CoverageDetails TEXT,
                    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
                )
            ''')

            # Create InventoryAlert table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS InventoryAlert (
                    AlertID INTEGER PRIMARY KEY AUTOINCREMENT,
                    MedicineID INTEGER,
                    AlertType TEXT,
                    Threshold INTEGER,
                    Status TEXT,
                    FOREIGN KEY (MedicineID) REFERENCES Medicine(MedicineID)
                )
            ''')

            conn.commit()
            self.logger.info("Database schema created successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Error creating schema: {e}")
            raise
        finally:
            conn.close()

    # MedicalStore methods
    def insert_medical_store(self, data: Dict[str, Any]) -> Optional[int]:
        """Insert a record into the MedicalStore table.

        Args:
            data: Dictionary with column names and values (e.g., StoreName, Address).

        Returns:
            The ID of the inserted record, or None if an error occurs.
        """
        self.logger.info("Inserting record into MedicalStore")
        required_fields = {'StoreName', 'Address', 'LicenseNumber'}
        if not required_fields.issubset(data):
            self.logger.error(f"Missing required fields: {required_fields - set(data)}")
            raise ValueError(f"Missing required fields: {required_fields - set(data)}")

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO MedicalStore ({columns}) VALUES ({placeholders})"

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, list(data.values()))
            conn.commit()
            record_id = cursor.lastrowid
            self.logger.info(f"Successfully inserted record into MedicalStore, ID: {record_id}")
            return record_id
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting into MedicalStore: {e}")
            return None
        finally:
            conn.close()

    def get_medical_store(self, condition: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve records from the MedicalStore table.

        Args:
            condition: Dictionary with column names and values to filter (optional).

        Returns:
            List of dictionaries containing the matching records.
        """
        self.logger.info("Retrieving records from MedicalStore")
        query = "SELECT * FROM MedicalStore"
        params = []
        if condition:
            conditions = [f"{key} = ?" for key in condition.keys()]
            query += " WHERE " + " AND ".join(conditions)
            params = list(condition.values())

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            self.logger.info(f"Retrieved {len(results)} records from MedicalStore")
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving from MedicalStore: {e}")
            return []
        finally:
            conn.close()

    def delete_medical_store(self, condition: Dict[str, Any]) -> int:
        """Delete records from the MedicalStore table.

        Args:
            condition: Dictionary with column names and values to filter.

        Returns:
            Number of rows deleted.
        """
        self.logger.info("Deleting records from MedicalStore")
        if not condition:
            self.logger.error("Condition dictionary cannot be empty")
            raise ValueError("Condition dictionary cannot be empty")

        conditions = [f"{key} = ?" for key in condition.keys()]
        query = f"DELETE FROM MedicalStore WHERE " + " AND ".join(conditions)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, list(condition.values()))
            conn.commit()
            row_count = cursor.rowcount
            self.logger.info(f"Deleted {row_count} records from MedicalStore")
            return row_count
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting from MedicalStore: {e}")
            return 0
        finally:
            conn.close()

    # Operator methods
    def insert_operator(self, data: Dict[str, Any]) -> Optional[int]:
        """Insert a record into the Operator table.

        Args:
            data: Dictionary with column names and values (e.g., Name, ContactInfo).

        Returns:
            The ID of the inserted record, or None if an error occurs.
        """
        self.logger.info("Inserting record into Operator")
        required_fields = {'Name'}
        if not required_fields.issubset(data):
            self.logger.error(f"Missing required fields: {required_fields - set(data)}")
            raise ValueError(f"Missing required fields: {required_fields - set(data)}")

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO Operator ({columns}) VALUES ({placeholders})"

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, list(data.values()))
            conn.commit()
            record_id = cursor.lastrowid
            self.logger.info(f"Successfully inserted record into Operator, ID: {record_id}")
            return record_id
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting into Operator: {e}")
            return None
        finally:
            conn.close()

    def get_operator(self, condition: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve records from the Operator table.

        Args:
            condition: Dictionary with column names and values to filter (optional).

        Returns:
            List of dictionaries containing the matching records.
        """
        self.logger.info("Retrieving records from Operator")
        query = "SELECT * FROM Operator"
        params = []
        if condition:
            conditions = [f"{key} = ?" for key in condition.keys()]
            query += "ulate WHERE " + " AND ".join(conditions)
            params = list(condition.values())

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            self.logger.info(f"Retrieved {len(results)} records from Operator")
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving from Operator: {e}")
            return []
        finally:
            conn.close()

    def delete_operator(self, condition: Dict[str, Any]) -> int:
        """Delete records from the Operator table.

        Args:
            condition: Dictionary with column names and values to filter.

        Returns:
            Number of rows deleted.
        """
        self.logger.info("Deleting records from Operator")
        if not condition:
            self.logger.error("Condition dictionary cannot be empty")
            raise ValueError("Condition dictionary cannot be empty")

        conditions = [f"{key} = ?" for key in condition.keys()]
        query = f"DELETE FROM Operator WHERE " + " AND ".join(conditions)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, list(condition.values()))
            conn.commit()
            row_count = cursor.rowcount
            self.logger.info(f"Deleted {row_count} records from Operator")
            return row_count
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting from Operator: {e}")
            return 0
        finally:
            conn.close()

    # Customer methods
    def insert_customer(self, data: Dict[str, Any]) -> Optional[int]:
        """Insert a record into the Customer table.

        Args:
            data: Dictionary with column names and values (e.g., Name, ContactInfo).

        Returns:
            The ID of the inserted record, or None if an error occurs.
        """
        self.logger.info("Inserting record into Customer")
        required_fields = {'Name'}
        if not required_fields.issubset(data):
            self.logger.error(f"Missing required fields: {required_fields - set(data)}")
            raise ValueError(f"Missing required fields: {required_fields - set(data)}")

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO Customer ({columns}) VALUES ({placeholders})"

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, list(data.values()))
            conn.commit()
            record_id = cursor.lastrowid
            self.logger.info(f"Successfully inserted record into Customer, ID: {record_id}")
            return record_id
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting into Customer: {e}")
            return None
        finally:
            conn.close()

    def get_customer(self, condition: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve records from the Customer table.

        Args:
            condition: Dictionary with column names and values to filter (optional).

        Returns:
            List of dictionaries containing the matching records.
        """
        self.logger.info("Retrieving records from Customer")
        query = "SELECT * FROM Customer"
        params = []
        if condition:
            conditions = [f"{key} = ?" for key in condition.keys()]
            query += " WHERE " + " AND ".join(conditions)
            params = list(condition.values())

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            self.logger.info(f"Retrieved {len(results)} records from Customer")
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving from Customer: {e}")
            return []
        finally:
            conn.close()

    def delete_customer(self, condition: Dict[str, Any]) -> int:
        """Delete records from the Customer table.

        Args:
            condition: Dictionary with column names and values to filter.

        Returns:
            Number of rows deleted.
        """
        self.logger.info("Deleting records from Customer")
        if not condition:
            self.logger.error("Condition dictionary cannot be empty")
            raise ValueError("Condition dictionary cannot be empty")

        conditions = [f"{key} = ?" for key in condition.keys()]
        query = f"DELETE FROM Customer WHERE " + " AND ".join(conditions)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, list(condition.values()))
            conn.commit()
            row_count = cursor.rowcount
            self.logger.info(f"Deleted {row_count} records from Customer")
            return row_count
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting from Customer: {e}")
            return 0
        finally:
            conn.close()

    # StorageLocation methods
    def insert_storage_location(self, data: Dict[str, Any]) -> Optional[int]:
        """Insert a record into the StorageLocation table.

        Args:
            data: Dictionary with column names and values (e.g., Label).

        Returns:
            The ID of the inserted record, or None if an error occurs.
        """
        self.logger.info("Inserting record into StorageLocation")
        required_fields = {'Label'}
        if not required_fields.issubset(data):
            self.logger.error(f"Missing required fields: {required_fields - set(data)}")
            raise ValueError(f"Missing required fields: {required_fields - set(data)}")

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO StorageLocation ({columns}) VALUES ({placeholders})"

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, list(data.values()))
            conn.commit()
            record_id = cursor.lastrowid
            self.logger.info(f"Successfully inserted record into StorageLocation, ID: {record_id}")
            return record_id
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting into StorageLocation: {e}")
            return None
        finally:
            conn.close()

    def get_storage_location(self, condition: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve records from the StorageLocation table.

        Args:
            condition: Dictionary with column names and values to filter (optional).

        Returns:
            List of dictionaries containing the matching records.
        """
        self.logger.info("Retrieving records from StorageLocation")
        query = "SELECT * FROM StorageLocation"
        params = []
        if condition:
            conditions = [f"{key} = ?" for key in condition.keys()]
            query += " WHERE " + " AND ".join(conditions)
            params = list(condition.values())

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            self.logger.info(f"Retrieved {len(results)} records from StorageLocation")
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving from StorageLocation: {e}")
            return []
        finally:
            conn.close()

    def delete_storage_location(self, condition: Dict[str, Any]) -> int:
        """Delete records from the StorageLocation table.

        Args:
            condition: Dictionary with column names and values to filter.

        Returns:
            Number of rows deleted.
        """
        self.logger.info("Deleting records from StorageLocation")
        if not condition:
            self.logger.error("Condition dictionary cannot be empty")
            raise ValueError("Condition dictionary cannot be empty")

        conditions = [f"{key} = ?" for key in condition.keys()]
        query = f"DELETE FROM StorageLocation WHERE " + " AND ".join(conditions)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, list(condition.values()))
            conn.commit()
            row_count = cursor.rowcount
            self.logger.info(f"Deleted {row_count} records from StorageLocation")
            return row_count
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting from StorageLocation: {e}")
            return 0
        finally:
            conn.close()

    # Medicine methods
    def insert_medicine(self, data: Dict[str, Any]) -> Optional[int]:
        """Insert a record into the Medicine table.

        Args:
            data: Dictionary with column names and values (e.g., Name, Price).

        Returns:
            The ID of the inserted record, or None if an error occurs.
        """
        self.logger.info("Inserting record into Medicine")
        required_fields = {'Name', 'Price', 'StockQuantity'}
        if not required_fields.issubset(data):
            self.logger.error(f"Missing required fields: {required_fields - set(data)}")
            raise ValueError(f"Missing required fields: {required_fields - set(data)}")

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO Medicine ({columns}) VALUES ({placeholders})"

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, list(data.values()))
            conn.commit()
            record_id = cursor.lastrowid
            self.logger.info(f"Successfully inserted record into Medicine, ID: {record_id}")
            return record_id
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting into Medicine: {e}")
            return None
        finally:
            conn.close()

    def get_medicine(self, condition: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve records from the Medicine table.

        Args:
            condition: Dictionary with column names and values to filter (optional).

        Returns:
            List of dictionaries containing the matching records.
        """
        self.logger.info("Retrieving records from Medicine")
        query = "SELECT * FROM Medicine"
        params = []
        if condition:
            conditions = [f"{key} = ?" for key in condition.keys()]
            query += " WHERE " + " AND ".join(conditions)
            params = list(condition.values())

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            self.logger.info(f"Retrieved {len(results)} records from Medicine")
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving from Medicine: {e}")
            return []
        finally:
            conn.close()

    def delete_medicine(self, condition: Dict[str, Any]) -> int:
        """Delete records from the Medicine table.

        Args:
            condition: Dictionary with column names and values to filter.

        Returns:
            Number of rows deleted.
        """
        self.logger.info("Deleting records from Medicine")
        if not condition:
            self.logger.error("Condition dictionary cannot be empty")
            raise ValueError("Condition dictionary cannot be empty")

        conditions = [f"{key} = ?" for key in condition.keys()]
        query = f"DELETE FROM Medicine WHERE " + " AND ".join(conditions)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, list(condition.values()))
            conn.commit()
            row_count = cursor.rowcount
            self.logger.info(f"Deleted {row_count} records from Medicine")
            return row_count
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting from Medicine: {e}")
            return 0
        finally:
            conn.close()

    # Purchase methods
    def insert_purchase(self, data: Dict[str, Any]) -> Optional[int]:
        """Insert a record into the Purchase table.

        Args:
            data: Dictionary with column names and values (e.g., DateOfPurchase, TotalAmount).

        Returns:
            The ID of the inserted record, or None if an error occurs.
        """
        self.logger.info("Inserting record into Purchase")
        required_fields = {'DateOfPurchase', 'TotalAmount'}
        if not required_fields.issubset(data):
            self.logger.error(f"Missing required fields: {required_fields - set(data)}")
            raise ValueError(f"Missing required fields: {required_fields - set(data)}")

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO Purchase ({columns}) VALUES ({placeholders})"

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, list(data.values()))
            conn.commit()
            record_id = cursor.lastrowid
            self.logger.info(f"Successfully inserted record into Purchase, ID: {record_id}")
            return record_id
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting into Purchase: {e}")
            return None
        finally:
            conn.close()

    def get_purchase(self, condition: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve records from the Purchase table.

        Args:
            condition: Dictionary with column names and values to filter (optional).

        Returns:
            List of dictionaries containing the matching records.
        """
        self.logger.info("Retrieving records from Purchase")
        query = "SELECT * FROM Purchase"
        params = []
        if condition:
            conditions = [f"{key} = ?" for key in condition.keys()]
            query += " WHERE " + " AND ".join(conditions)
            params = list(condition.values())

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            self.logger.info(f"Retrieved {len(results)} records from Purchase")
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving from Purchase: {e}")
            return []
        finally:
            conn.close()

    def delete_purchase(self, condition: Dict[str, Any]) -> int:
        """Delete records from the Purchase table.

        Args:
            condition: Dictionary with column names and values to filter.

        Returns:
            Number of rows deleted.
        """
        self.logger.info("Deleting records from Purchase")
        if not condition:
            self.logger.error("Condition dictionary cannot be empty")
            raise ValueError("Condition dictionary cannot be empty")

        conditions = [f"{key} = ?" for key in condition.keys()]
        query = f"DELETE FROM Purchase WHERE " + " AND ".join(conditions)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, list(condition.values()))
            conn.commit()
            row_count = cursor.rowcount
            self.logger.info(f"Deleted {row_count} records from Purchase")
            return row_count
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting from Purchase: {e}")
            return 0
        finally:
            conn.close()

    # PurchaseItem methods
    def insert_purchase_item(self, data: Dict[str, Any]) -> Optional[int]:
        """Insert a record into the PurchaseItem table.

        Args:
            data: Dictionary with column names and values (e.g., PurchaseID, MedicineID).

        Returns:
            The ID of the inserted record, or None if an error occurs.
        """
        self.logger.info("Inserting record into PurchaseItem")
        required_fields = {'PurchaseID', 'MedicineID', 'Quantity', 'PricePerUnit'}
        if not required_fields.issubset(data):
            self.logger.error(f"Missing required fields: {required_fields - set(data)}")
            raise ValueError(f"Missing required fields: {required_fields - set(data)}")

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO PurchaseItem ({columns}) VALUES ({placeholders})"

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, list(data.values()))
            conn.commit()
            record_id = cursor.lastrowid
            self.logger.info(f"Successfully inserted record into PurchaseItem, ID: {record_id}")
            return record_id
        except sqlite3.Error as e:
            self.logger.error(f"Error inserting into PurchaseItem: {e}")
            return None
        finally:
            conn.close()

    def get_purchase_item(self, condition: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve records from the PurchaseItem table.

        Args:
            condition: Dictionary with column names and values to filter (optional).

        Returns:
            List of dictionaries containing the matching records.
        """
        self.logger.info("Retrieving records from PurchaseItem")
        query = "SELECT * FROM PurchaseItem"
        params = []
        if condition:
            conditions = [f"{key} = ?" for key in condition.keys()]
            query += " WHERE " + " AND ".join(conditions)
            params = list(condition.values())

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            self.logger.info(f"Retrieved {len(results)} records from PurchaseItem")
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving from PurchaseItem: {e}")
            return []
        finally:
            conn.close()

    def delete_purchase_item(self, condition: Dict[str, Any]) -> int:
        """Delete records from the PurchaseItem table.

        Args:
            condition: Dictionary with column names and values to filter.

        Returns:
            Number of rows deleted.
        """
        self.logger.info("Deleting records from PurchaseItem")
        if not condition:
            self.logger.error("Condition dictionary cannot be empty")
            raise ValueError("Condition dictionary cannot be empty")

        conditions = [f"{key} = ?" for key in condition.keys()]
        query = f"DELETE FROM PurchaseItem WHERE " + " AND ".join(conditions)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, list(condition.values()))
            conn.commit()
            row_count = cursor.rowcount
            self.logger.info(f"Deleted {row_count} records from PurchaseItem")
            return row_count
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting from PurchaseItem: {e}")
            return 0
        finally:
            conn.close()

    def add_batch(self, invoice_number: str, supplier: str, batch_number: str, 
                 batch_size: int, expiry_date: datetime, storage_location: str, 
                 barcode: Optional[str] = None) -> Optional[int]:
        """Add a new batch record.

        Args:
            invoice_number: The invoice number for this batch
            supplier: The supplier's name
            batch_number: The batch number
            batch_size: Total number of items in the batch
            expiry_date: Expiry date for the batch
            storage_location: Where the batch is stored
            barcode: Optional barcode for the batch

        Returns:
            The ID of the inserted batch record, or None if an error occurs
        """
        self.logger.info("Adding new batch record")
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO Batch (
                    InvoiceNumber, Supplier, BatchNumber, BatchSize,
                    ExpiryDate, StorageLocation, Barcode
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_number, supplier, batch_number, batch_size,
                expiry_date, storage_location, barcode
            ))
            
            batch_id = cursor.lastrowid
            conn.commit()
            self.logger.info(f"Successfully added batch with ID: {batch_id}")
            return batch_id
        except sqlite3.Error as e:
            self.logger.error(f"Error adding batch: {e}")
            return None
        finally:
            conn.close()

    def get_batch_by_barcode(self, barcode: str) -> Optional[dict]:
        """Get batch details by barcode.

        Args:
            barcode: The barcode to look up

        Returns:
            Dictionary containing batch details and its items, or None if not found
        """
        self.logger.info(f"Looking up batch with barcode: {barcode}")
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get batch details
            cursor.execute("""
                SELECT * FROM Batch WHERE Barcode = ?
            """, (barcode,))
            
            batch = cursor.fetchone()
            if not batch:
                return None
                
            batch_dict = dict(batch)
            
            # Get items in this batch
            cursor.execute("""
                SELECT m.* FROM Medicine m
                JOIN BatchItem bi ON m.MedicineID = bi.MedicineID
                WHERE bi.BatchID = ?
            """, (batch_dict['BatchID'],))
            
            items = [dict(row) for row in cursor.fetchall()]
            batch_dict['items'] = items
            
            return batch_dict
        except sqlite3.Error as e:
            self.logger.error(f"Error looking up batch: {e}")
            return None
        finally:
            conn.close()

    def add_batch_item(self, batch_id: int, medicine_id: int, quantity: int) -> Optional[int]:
        """Add an item to a batch.

        Args:
            batch_id: The ID of the batch
            medicine_id: The ID of the medicine
            quantity: The quantity of this medicine in the batch

        Returns:
            The ID of the inserted batch item record, or None if an error occurs
        """
        self.logger.info(f"Adding item {medicine_id} to batch {batch_id}")
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO BatchItem (BatchID, MedicineID, Quantity)
                VALUES (?, ?, ?)
            """, (batch_id, medicine_id, quantity))
            
            item_id = cursor.lastrowid
            conn.commit()
            self.logger.info(f"Successfully added batch item with ID: {item_id}")
            return item_id
        except sqlite3.Error as e:
            self.logger.error(f"Error adding batch item: {e}")
            return None
        finally:
            conn.close()


if __name__ == '__main__':
    db = SQLiteDatabase('medical_store.db')