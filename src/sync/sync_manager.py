import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import requests
from ..utils.loggers import LoggerFactory

class SyncManager:
    def __init__(self, store_id: str, server_url: str, local_db_path: str):
        """Initialize the sync manager.
        
        Args:
            store_id: Unique identifier for the store
            server_url: URL of the main server
            local_db_path: Path to local SQLite database
        """
        self.store_id = store_id
        self.server_url = server_url.rstrip('/')
        self.local_db_path = local_db_path
        
        # Set up logger
        base_dir = os.path.abspath(os.path.dirname(__file__))
        log_dir = os.path.join(base_dir, "..", "..", "results", "logs")
        self.logger = LoggerFactory("SyncLogger", log_dir, "sync").get_logger()
        
        # Initialize sync queue
        self.sync_queue = []
        self.last_sync_time = None
        self.sync_token = None

    def connect_to_server(self) -> bool:
        """Establish connection with the main server and get sync token."""
        try:
            response = requests.post(
                f"{self.server_url}/api/sync/connect",
                json={"store_id": self.store_id}
            )
            if response.status_code == 200:
                data = response.json()
                self.sync_token = data.get("token")
                self.last_sync_time = data.get("last_sync")
                self.logger.info(f"Connected to server. Last sync: {self.last_sync_time}")
                return True
            else:
                self.logger.error(f"Failed to connect to server: {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Error connecting to server: {e}")
            return False

    def queue_change(self, table: str, operation: str, data: Dict) -> None:
        """Queue a database change for synchronization.
        
        Args:
            table: Name of the table being modified
            operation: Type of operation (insert/update/delete)
            data: The data being changed
        """
        change = {
            "timestamp": datetime.now().isoformat(),
            "table": table,
            "operation": operation,
            "data": data
        }
        self.sync_queue.append(change)
        self.logger.info(f"Queued change: {operation} on {table}")

    def sync_changes(self) -> bool:
        """Synchronize queued changes with the main server."""
        if not self.sync_token:
            if not self.connect_to_server():
                return False

        try:
            # Get changes since last sync
            response = requests.get(
                f"{self.server_url}/api/sync/changes",
                headers={"Authorization": f"Bearer {self.sync_token}"},
                params={"since": self.last_sync_time}
            )
            
            if response.status_code == 200:
                server_changes = response.json().get("changes", [])
                self._resolve_conflicts(server_changes)
                
                # Send local changes
                if self.sync_queue:
                    response = requests.post(
                        f"{self.server_url}/api/sync/push",
                        headers={"Authorization": f"Bearer {self.sync_token}"},
                        json={"changes": self.sync_queue}
                    )
                    
                    if response.status_code == 200:
                        self.sync_queue = []
                        self.last_sync_time = datetime.now().isoformat()
                        self.logger.info("Successfully synced changes")
                        return True
                    else:
                        self.logger.error(f"Failed to push changes: {response.text}")
                        return False
                return True
            else:
                self.logger.error(f"Failed to get server changes: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during sync: {e}")
            return False

    def _resolve_conflicts(self, server_changes: List[Dict]) -> None:
        """Resolve conflicts between local and server changes.
        
        Args:
            server_changes: List of changes from the server
        """
        # TODO: Implement conflict resolution logic
        # For now, server changes take precedence
        for change in server_changes:
            self.logger.info(f"Applying server change: {change['operation']} on {change['table']}")
            # Apply server change to local database
            # This will be implemented when we modify the database schema

    def start_sync_loop(self, interval: int = 300) -> None:
        """Start continuous synchronization loop.
        
        Args:
            interval: Sync interval in seconds (default: 5 minutes)
        """
        while True:
            try:
                self.sync_changes()
                time.sleep(interval)
            except Exception as e:
                self.logger.error(f"Error in sync loop: {e}")
                time.sleep(60)  # Wait a minute before retrying 