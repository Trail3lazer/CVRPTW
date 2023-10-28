from dataclasses import dataclass, asdict
from typing import TypeVar, Generic, List
from datetime import datetime

KT = TypeVar('KT')
VT = TypeVar('VT')

@dataclass
class Entry(Generic[KT,VT]):
    key: KT
    value: VT
    
class DeliveryStatus():
    at_hub = "at the hub"
    en_route = "en route"
    delivered = "delivered"    

@dataclass
class Location:
    location_id: int
    name: int
    address: str
    status: DeliveryStatus
    deadline: datetime
    stop_number: int
    truck: int
    package_ids: List[int]
    
    def __str__(self):
        return f"{asdict(self)}"

@dataclass
class Package: 
    package_id: int
    location_id: int
    address: str
    city: str
    state: str
    postal_code: str
    package_weight: str
    notes: str
    
    def __str__(self):
        return f"{asdict(self)}"
    
