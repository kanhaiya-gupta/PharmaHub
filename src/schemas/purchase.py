from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator

class PurchaseItemBase(BaseModel):
    medicine_id: int
    quantity: int = Field(..., gt=0)
    price_per_unit: float = Field(..., gt=0)

class PurchaseItemCreate(PurchaseItemBase):
    pass

class PurchaseItemInDB(PurchaseItemBase):
    purchase_item_id: int
    purchase_id: int

    class Config:
        orm_mode = True

class PurchaseBase(BaseModel):
    customer_id: Optional[int] = None
    operator_id: Optional[int] = None
    date_of_purchase: datetime = Field(default_factory=datetime.now)
    total_amount: float = Field(..., gt=0)
    items: List[PurchaseItemCreate]

    @validator('total_amount')
    def validate_total_amount(cls, v, values):
        if 'items' in values:
            calculated_total = sum(item.quantity * item.price_per_unit for item in values['items'])
            if abs(v - calculated_total) > 0.01:  # Allow for small floating-point differences
                raise ValueError('Total amount does not match sum of items')
        return v

class PurchaseCreate(PurchaseBase):
    pass

class PurchaseUpdate(BaseModel):
    customer_id: Optional[int] = None
    operator_id: Optional[int] = None
    items: Optional[List[PurchaseItemCreate]] = None

class PurchaseInDB(PurchaseBase):
    purchase_id: int
    items: List[PurchaseItemInDB]

    class Config:
        orm_mode = True 