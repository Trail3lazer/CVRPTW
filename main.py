
# Studend ID: 010771776

import datetime
from typing import List
from models import Package
from datalayer import get_locations, get_package_lookup

drivers = 2
trucks = 3
truck_speed = 18
max_load = 16
start_time = datetime.time(8)
loaded_packages = [[],[],[]]
 
def calc_distance(matrix, route):
    distance = 0
    for i,location in enumerate(route):
        if i == 0:
            continue
        prev_location = route[i-1]
        weight = matrix[location][prev_location]
        distance += weight

def get_nearest(locationId: int, weights: List[List[float]]):
    nearestId,min = None,float("inf")
    for id, weight in enumerate(weights[locationId]):
        if weight < min:
            nearestId = id
            min = weight
    return nearestId

def set_location_col_to_inf(locationId: int, weights: List[List[float]]):
    inf = float("inf")
    for l in weights:
        l[locationId] = inf

def main():
    locations, weights = get_locations()
    packages = get_package_lookup(locations)
    print(locations)
    print(packages)
    return
    address_count = len(locations)
    deliveries = [Package(a.key, a.value) for a in locations.entries]

    while len([d for d in deliveries if d.stop_number is None]) < address_count:
        locationId = 0
        load = 0
        route = [locationId]
        deliveries[locationId] = True
        
main()
