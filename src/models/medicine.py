from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Medicine:
    medicine_id: Optional[int]
    name: str
    brand: Optional[str]
    batch_number: Optional[str]
    expiry_date: Optional[datetime]
    price: float
    stock_quantity: int
    type: Optional[str]
    requires_prescription: bool
    schedule_category: Optional[str]
    date_added: Optional[datetime]
    storage_location_id: Optional[int]

    def to_dict(self) -> dict:
        return {
            'MedicineID': self.medicine_id,
            'Name': self.name,
            'Brand': self.brand,
            'BatchNumber': self.batch_number,
            'ExpiryDate': self.expiry_date.isoformat() if self.expiry_date else None,
            'Price': self.price,
            'StockQuantity': self.stock_quantity,
            'Type': self.type,
            'RequiresPrescription': self.requires_prescription,
            'ScheduleCategory': self.schedule_category,
            'DateAdded': self.date_added.isoformat() if self.date_added else None,
            'StorageLocationID': self.storage_location_id
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Medicine':
        return cls(
            medicine_id=data.get('MedicineID'),
            name=data['Name'],
            brand=data.get('Brand'),
            batch_number=data.get('BatchNumber'),
            expiry_date=datetime.fromisoformat(data['ExpiryDate']) if data.get('ExpiryDate') else None,
            price=data['Price'],
            stock_quantity=data['StockQuantity'],
            type=data.get('Type'),
            requires_prescription=data.get('RequiresPrescription', False),
            schedule_category=data.get('ScheduleCategory'),
            date_added=datetime.fromisoformat(data['DateAdded']) if data.get('DateAdded') else None,
            storage_location_id=data.get('StorageLocationID')
        ) 