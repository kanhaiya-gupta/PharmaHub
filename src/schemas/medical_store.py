from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class MedicalStoreBase(BaseModel):
    store_name: str = Field(..., min_length=1, max_length=100)
    address: str = Field(..., min_length=1, max_length=200)
    contact_number: Optional[str] = Field(None, max_length=20)
    license_number: str = Field(..., min_length=1, max_length=50)
    opening_date: Optional[datetime] = None

class MedicalStoreCreate(MedicalStoreBase):
    pass

class MedicalStoreUpdate(MedicalStoreBase):
    store_name: Optional[str] = Field(None, min_length=1, max_length=100)
    address: Optional[str] = Field(None, min_length=1, max_length=200)
    license_number: Optional[str] = Field(None, min_length=1, max_length=50)

class MedicalStoreInDB(MedicalStoreBase):
    store_id: int

    class Config:
        orm_mode = True 