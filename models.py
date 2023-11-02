from dataclasses import dataclass
import enum
import time
from typing import TypeVar, Generic, List
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



@dataclass
class PackageTimeline:
    at_hub: time
    enroute: time
    delivered: time



class DeliveryStatus(enum.Enum):
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
    timeline: PackageTimeline



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
