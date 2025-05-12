from dataclasses import dataclass
from typing import Optional

@dataclass
class Operator:
    operator_id: Optional[int]
    name: str
    contact_info: Optional[str]
    role: Optional[str]
    assigned_store_id: Optional[int]

    def to_dict(self) -> dict:
        return {
            'OperatorID': self.operator_id,
            'Name': self.name,
            'ContactInfo': self.contact_info,
            'Role': self.role,
            'AssignedStoreID': self.assigned_store_id
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Operator':
        return cls(
            operator_id=data.get('OperatorID'),
            name=data['Name'],
            contact_info=data.get('ContactInfo'),
            role=data.get('Role'),
            assigned_store_id=data.get('AssignedStoreID')
        ) 