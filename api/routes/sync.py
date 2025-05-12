from fastapi import APIRouter, HTTPException, Depends, Header
from typing import List, Dict, Optional
from datetime import datetime
import jwt
from ...src.utils.loggers import LoggerFactory
import os

router = APIRouter(prefix="/api/sync", tags=["sync"])

# Set up logger
base_dir = os.path.abspath(os.path.dirname(__file__))
log_dir = os.path.join(base_dir, "..", "..", "results", "logs")
logger = LoggerFactory("SyncAPILogger", log_dir, "sync_api").get_logger()

# Secret key for JWT tokens (should be in environment variables in production)
SECRET_KEY = "your-secret-key-here"  # TODO: Move to environment variables

async def verify_token(authorization: str = Header(...)) -> str:
    """Verify the JWT token and return the store ID."""
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("store_id")
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/connect")
async def connect_store(store_data: Dict):
    """Connect a store to the sync system and get a token."""
    try:
        store_id = store_data.get("store_id")
        if not store_id:
            raise HTTPException(status_code=400, detail="Store ID is required")

        # Generate JWT token
        token = jwt.encode(
            {
                "store_id": store_id,
                "exp": datetime.utcnow().timestamp() + 86400  # 24 hours
            },
            SECRET_KEY,
            algorithm="HS256"
        )

        # Get last sync time from database
        # TODO: Implement database query
        last_sync = datetime.utcnow().isoformat()

        return {
            "token": token,
            "last_sync": last_sync
        }
    except Exception as e:
        logger.error(f"Store connection failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect store")

@router.get("/changes")
async def get_changes(since: str, store_id: str = Depends(verify_token)):
    """Get changes since the last sync."""
    try:
        # TODO: Query database for changes since the given timestamp
        changes = []  # This will be populated from the database
        
        return {"changes": changes}
    except Exception as e:
        logger.error(f"Failed to get changes: {e}")
        raise HTTPException(status_code=500, detail="Failed to get changes")

@router.post("/push")
async def push_changes(changes_data: Dict, store_id: str = Depends(verify_token)):
    """Push local changes to the server."""
    try:
        changes = changes_data.get("changes", [])
        if not changes:
            return {"status": "success", "message": "No changes to push"}

        # TODO: Apply changes to the database
        # This will be implemented when we modify the database schema

        return {"status": "success", "message": f"Pushed {len(changes)} changes"}
    except Exception as e:
        logger.error(f"Failed to push changes: {e}")
        raise HTTPException(status_code=500, detail="Failed to push changes")

@router.get("/status")
async def get_sync_status(store_id: str = Depends(verify_token)):
    """Get the current sync status for a store."""
    try:
        # TODO: Get sync status from database
        return {
            "store_id": store_id,
            "last_sync": datetime.utcnow().isoformat(),
            "status": "connected",
            "pending_changes": 0
        }
    except Exception as e:
        logger.error(f"Failed to get sync status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sync status") 