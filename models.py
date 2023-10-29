from dataclasses import dataclass, asdict
from typing import TypeVar, Generic, List
from datetime import datetime



# Simpler print format for datetimes
def __strfdatetime(value):
    if not value: return None
    return value.strftime("%Y-%m-%D %H:%M:%S")



# setup key value type vars
KT = TypeVar('KT')
VT = TypeVar('VT')



# Use dataclass property to generate default constructor
# for class fields.
@dataclass
class Entry(Generic[KT,VT]):
    key: KT
    value: VT



# Enum like class used instead of enum because it prints cleaner.
class DeliveryStatus():
    at_hub = "at the hub"
    en_route = "en route"
    delivered = "delivered"    



@dataclass
class Package: 
    package_id: int
    location_id: int
    package_weight: str
    notes: str
    status: DeliveryStatus
    deadline: datetime
        
    # Simpler print format for fields, excludes dataclass auto properties.
    def __str__(self):
        return f"{asdict(self)}"



# Put most of the address properties in another object to 
# make routing easier and reduce redundancy.
@dataclass
class Location:
    location_id: int
    name: int
    address: str
    city: str
    state: str
    postal_code: str
    package_ids: List[int]
    
    # Simpler print format for fields, excludes dataclass auto properties.
    def __str__(self):
        fieldlist = asdict(self)
        fieldlist["deadline"] = __strfdatetime(self.deadline)
        return f"{fieldlist}"


@dataclass
class Delivery:
    delivery_time: datetime
    route_index: int
    truck: int
    location_id: int
    package_ids: List[int]
    
    # Simpler print format for fields, excludes dataclass auto properties.
    def __str__(self):
        fieldlist = asdict(self)
        fieldlist["delivery_time"] = __strfdatetime(self.delivery_time)
        return f"{fieldlist}"
    