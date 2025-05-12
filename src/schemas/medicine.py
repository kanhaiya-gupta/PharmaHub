from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator

class MedicineBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    batch_number: Optional[str] = Field(None, max_length=50)
    expiry_date: Optional[datetime] = None
    price: float = Field(..., gt=0)
    stock_quantity: int = Field(..., ge=0)
    type: Optional[str] = Field(None, max_length=50)
    requires_prescription: bool = False
    schedule_category: Optional[str] = Field(None, max_length=20)
    storage_location_id: Optional[int] = None

    @validator('expiry_date')
    def validate_expiry_date(cls, v):
        if v and v < datetime.now():
            raise ValueError('Expiry date cannot be in the past')
        return v

class MedicineCreate(MedicineBase):
    pass

class MedicineUpdate(MedicineBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)

class MedicineInDB(MedicineBase):
    medicine_id: int
    date_added: datetime

    class Config:
        orm_mode = True 