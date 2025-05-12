# main.py
"""Main entry point for running the PharmaHub server."""

import os
import socket
import sys
import argparse
from datetime import datetime

import qrcode
import uvicorn
from src.utils.loggers import LoggerFactory
from src.sync.sync_manager import SyncManager

# Add the current directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Set up logger
base_dir = os.path.abspath(os.path.dirname(__file__))
log_dir = os.path.join(base_dir, "results", "logs")
logger = LoggerFactory("MainLogger", log_dir, "main").get_logger()

def get_local_ip() -> str:
    """Detect the local IP address of the system."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        logger.warning(f"Could not detect local IP: {e}. Falling back to 127.0.0.1")
        return "127.0.0.1"

def generate_qr_code(url: str, filename: str = "static/server_qr.png") -> None:
    """Generate a QR code for the given URL."""
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)
        logger.info(f"QR code generated and saved as '{filename}'")
    except Exception as e:
        logger.error(f"Failed to generate QR code: {e}")

def initialize_database():
    """Initialize the database with required data."""
    try:
        from src.database.init_db import init_database
        if init_database():
            logger.info("Database initialized successfully")
            return True
        else:
            logger.error("Failed to initialize database")
            return False
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        return False

def run_store_mode(store_id: str, server_url: str):
    """Run the application in store mode."""
    try:
        # Initialize local database
        if not initialize_database():
            logger.error("Failed to initialize local database")
            sys.exit(1)

        # Initialize sync manager
        local_db_path = os.path.join(base_dir, "results", f"store_{store_id}.db")
        sync_manager = SyncManager(store_id, server_url, local_db_path)

        # Start sync loop in a separate thread
        import threading
        sync_thread = threading.Thread(
            target=sync_manager.start_sync_loop,
            daemon=True
        )
        sync_thread.start()

        # Start the store server
        host = "0.0.0.0"
        port = 8000
        logger.info(f"Starting store server on http://{host}:{port}")
        uvicorn.run("api.api:app", host=host, port=port, reload=True)

    except Exception as e:
        logger.error(f"Error in store mode: {e}")
        sys.exit(1)

def run_server_mode(host: str, port: int):
    """Run the application in server mode."""
    try:
        # Initialize main database
        if not initialize_database():
            logger.error("Failed to initialize main database")
            sys.exit(1)

        # Start the main server
        logger.info(f"Starting main server on http://{host}:{port}")
        uvicorn.run("api.api:app", host=host, port=port, reload=True)

    except Exception as e:
        logger.error(f"Error in server mode: {e}")
        sys.exit(1)

def run_dev_mode():
    """Run the application in development mode."""
    try:
        # Initialize database
        if not initialize_database():
            logger.error("Failed to initialize database")
            sys.exit(1)

        # Start the development server
        host = "127.0.0.1"
        port = 8000
        logger.info(f"Starting development server on http://{host}:{port}")
        uvicorn.run("api.api:app", host=host, port=port, reload=True)

    except Exception as e:
        logger.error(f"Error in development mode: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PharmaHub Server")
    parser.add_argument("mode", choices=["dev", "store", "server"],
                      help="Run mode: dev, store, or server")
    parser.add_argument("--store-id", help="Store ID for store mode")
    parser.add_argument("--server-url", help="Main server URL for store mode")
    parser.add_argument("--host", default="0.0.0.0", help="Host for server mode")
    parser.add_argument("--port", type=int, default=8000, help="Port for server mode")

    args = parser.parse_args()

    if args.mode == "dev":
        run_dev_mode()
    elif args.mode == "store":
        if not args.store_id or not args.server_url:
            logger.error("Store ID and server URL are required for store mode")
            sys.exit(1)
        run_store_mode(args.store_id, args.server_url)
    elif args.mode == "server":
        run_server_mode(args.host, args.port)