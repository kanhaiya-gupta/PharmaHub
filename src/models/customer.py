from dataclasses import dataclass
from typing import Optional

@dataclass
class Customer:
    customer_id: Optional[int]
    name: str
    contact_info: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    address: Optional[str]

    def to_dict(self) -> dict:
        return {
            'CustomerID': self.customer_id,
            'Name': self.name,
            'ContactInfo': self.contact_info,
            'Age': self.age,
            'Gender': self.gender,
            'Address': self.address
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Customer':
        return cls(
            customer_id=data.get('CustomerID'),
            name=data['Name'],
            contact_info=data.get('ContactInfo'),
            age=data.get('Age'),
            gender=data.get('Gender'),
            address=data.get('Address')
        ) 