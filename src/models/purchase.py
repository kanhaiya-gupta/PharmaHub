from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class PurchaseItem:
    purchase_item_id: Optional[int]
    purchase_id: Optional[int]
    medicine_id: int
    quantity: int
    price_per_unit: float

    def to_dict(self) -> dict:
        return {
            'PurchaseItemID': self.purchase_item_id,
            'PurchaseID': self.purchase_id,
            'MedicineID': self.medicine_id,
            'Quantity': self.quantity,
            'PricePerUnit': self.price_per_unit
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PurchaseItem':
        return cls(
            purchase_item_id=data.get('PurchaseItemID'),
            purchase_id=data.get('PurchaseID'),
            medicine_id=data['MedicineID'],
            quantity=data['Quantity'],
            price_per_unit=data['PricePerUnit']
        )

@dataclass
class Purchase:
    purchase_id: Optional[int]
    customer_id: Optional[int]
    operator_id: Optional[int]
    date_of_purchase: datetime
    total_amount: float
    items: List[PurchaseItem]

    def to_dict(self) -> dict:
        return {
            'PurchaseID': self.purchase_id,
            'CustomerID': self.customer_id,
            'OperatorID': self.operator_id,
            'DateOfPurchase': self.date_of_purchase.isoformat(),
            'TotalAmount': self.total_amount
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Purchase':
        return cls(
            purchase_id=data.get('PurchaseID'),
            customer_id=data.get('CustomerID'),
            operator_id=data.get('OperatorID'),
            date_of_purchase=datetime.fromisoformat(data['DateOfPurchase']),
            total_amount=data['TotalAmount'],
            items=[]  # Items need to be loaded separately
        ) 