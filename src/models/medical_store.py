from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class MedicalStore:
    store_id: Optional[int]
    store_name: str
    address: str
    contact_number: Optional[str]
    license_number: str
    opening_date: Optional[datetime]

    def to_dict(self) -> dict:
        return {
            'StoreID': self.store_id,
            'StoreName': self.store_name,
            'Address': self.address,
            'ContactNumber': self.contact_number,
            'LicenseNumber': self.license_number,
            'OpeningDate': self.opening_date.isoformat() if self.opening_date else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'MedicalStore':
        return cls(
            store_id=data.get('StoreID'),
            store_name=data['StoreName'],
            address=data['Address'],
            contact_number=data.get('ContactNumber'),
            license_number=data['LicenseNumber'],
            opening_date=datetime.fromisoformat(data['OpeningDate']) if data.get('OpeningDate') else None
        ) 