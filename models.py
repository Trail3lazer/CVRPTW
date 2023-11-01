from dataclasses import dataclass
from typing import TypeVar, Generic, List
from datetime import datetime


def strfdatetime(value):
    """Simpler print format for datetimes. O[1]

    Args:
        value (datetime): The datetime needing to be converted to string.

    Returns:
        str: The datetime formatted like hh:mm:ss
    """

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


class DeliveryStatus:
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
    delivery_time: datetime
    earliest: datetime
    latest: datetime


#
@dataclass
class Location:
    """Contains most of the address properties to
    make routing easier and reduce redundancy."""

    location_id: int
    name: int
    address: str
    city: str
    state: str
    postal_code: str
    package_ids: List[int]
    earliest: datetime
    latest: datetime


@dataclass
class Stop:
    stop_time: datetime
    travel_distance: float
    location: Location
    reason: str
