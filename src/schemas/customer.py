from typing import Optional
from pydantic import BaseModel, Field, validator

class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    contact_info: Optional[str] = Field(None, max_length=50)
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[str] = Field(None, max_length=10)
    address: Optional[str] = Field(None, max_length=200)

    @validator('gender')
    def validate_gender(cls, v):
        if v and v.lower() not in ['male', 'female', 'other']:
            raise ValueError('Gender must be male, female, or other')
        return v

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100)

class CustomerInDB(CustomerBase):
    customer_id: int

    class Config:
        orm_mode = True 