from dataclasses import dataclass
import enum
import time
from typing import TypeVar, Generic, List, TypeVarTuple
from datetime import datetime


def strfdatetime(value: datetime):
    '''Simpler print format for datetimes. O(n)

    Args:
        value (datetime): The datetime needing to be converted to string.
    Returns:
        str: The datetime formatted like hh:mm:ss

    '''

    if not value:
        return None
    return value.strftime("%H:%M:%S")


KT = TypeVar("KT")
VT = TypeVar("VT")



@dataclass
class Entry(Generic[KT, VT]):
    key: KT
    value: VT



class StopReason:
    loading = "loading truck"
    delivery = "delivery"



class DeliveryStatus(enum.Enum):
    Airport = "Airport"
    hub = "hub"
    enroute = "enroute"
    delivered = "delivered"



@dataclass
class Package:
    package_id: int
    location_id: int
    weight: str
    notes: str
    earliest: datetime
    latest: datetime
    status: DeliveryStatus

    def copy(self):
        return Package(
            package_id=self.package_id,
            location_id=self.location_id,
            weight=self.weight,
            notes=self.notes,
            earliest=self.earliest,
            latest=self.latest,
            status=self.status,
        )



@dataclass
class PackageUpdate:
    timestamp: datetime
    package: Package



@dataclass
class Location:
    """Contains most of the address properties to
    make routing easier and reduce redundancy."""

    location_id: int
    name: str
    address: str
    city: str
    state: str
    postal_code: str
    package_ids: List[int]
    earliest: datetime
    latest: datetime
    truck_id: int = None


@dataclass
class Stop:
    stop_time: datetime
    travel_distance: float
    location: Location
    reason: str
