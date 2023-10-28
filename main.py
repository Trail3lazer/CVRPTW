
# Studend ID: 010771776

from datetime import datetime
from typing import List
from hash_table import Dictionary
from models import Location, Package
from datalayer import get_data

# Setup global constants.
DRIVERS = 2
MPH = 18
MAX_LOAD = 16
TRUCKS = [[],[7,8,17,19,20,21],[11,13,15,24]]


# Setup global variables.
current_time = datetime.today().replace(hour = 8, 
                                      minute = 0, 
                                      second = 0, 
                                      microsecond = 0)



# Calculate the total route distance.
# Having a separate method reduces nesting and reading complexity.
def calc_distance(matrix: List[List[float]], route: List[int]):
    
    # Set starting distance to 0.
    total = 0
    
    # Enumerate to be able to access previous location.
    for i,location_id in enumerate(route):
        
        # If it's the first stop, skip it.
        if i == 0:
            continue
        
        # get the distance between the current stop and the previous 
        # and add it to the total 
        prev_location_id = route[i-1]
        distance = matrix[location_id][prev_location_id]
        total += distance



# Find the nearest location that's on the truck's schedule and hasn't been visited yet.
# Having a separate method reduces nesting and reading complexity.
def get_nearest(location_id: int, 
                truck_schedule: List[int], 
                locations: Dictionary[int, Location],
                matrix: List[List[float]]):
    nearestId,min = None,float("inf")
    for id, weight in enumerate(matrix[location_id]):
        if id not in truck_schedule: continue
        if weight < min:
            nearestId = id
            min = weight
    return nearestId



def set_location_col_to_inf(locationId: int, weights: List[List[float]]):
    inf = float("inf")
    for l in weights:
        l[locationId] = inf

def main():
    locations, matrix, packages = get_data()
    
    address_count = len(locations)
    for l in sorted(locations.values, key=lambda e: e.location_id):
        print(f'{{ location: {l.location_id}, zip: {l.postal_code}, package: {l.package_ids} }}')
        
    groups = [[13,14,15,16,19,20,21],[3,18,36,38],[6,25,26,28,32]]
    
    initial_loads = [[],[],[]]
    truck_loads = [[],[],[]]
    
    
    for g in groups:
        for p_id in g:
            package_location_id = packages[p_id].location_id
            for i in range(len(initial_loads)):
                if package_location_id not in initial_loads[i]:
                    initial_loads[i].append(package_location_id)
                    break
    
    for p in packages.values:
        already_stored = False
        for t in initial_loads:
            if p.location_id in t:
                already_stored = True
                break
            
        if already_stored: continue
        
        for i,t in enumerate(initial_loads):
            matched = None
            for l_id in t:
                if locations[l_id].postal_code == locations[p.location_id].postal_code:
                    truck_loads[i].append(p.location_id)
                    break
    
    print(initial_loads, truck_loads)
    """
    delivered = [d for d in locations if d.delivery_time is not None]
    while len(delivered) < address_count:
        locationId = 0
        load = 0
        route = [locationId]
        locations[locationId].delivery_time = current_time
        delivered = [d for d in locations if d.delivery_time is not None]
    """
main()
