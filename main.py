
# Studend ID: 010771776

from datetime import datetime, timedelta
from typing import List
from hash_table import Dictionary
from models import Location, Package
from datalayer import get_data



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



def set_location_col_to_inf(locationId: int, weights: List[List[float]]):
    inf = float("inf")
    for l in weights:
        l[locationId] = inf



def get_delivered(locations: Dictionary[int, Location]):
    return [d for d in locations if d.delivery_time is not None]



def route_load(start: int, load: List[int], matrix: List[List[float]]):
    current = start
    route = [start]
    cost = 0
    while 0 < len(load):
        next_location = None
        closest_dist = float("inf")
        
        for other in load:
            if other is None: continue
            distance = matrix[current][other]
            if closest_dist > distance:
                closest_dist = distance
                next_location = other
        
        assert next_location is not None
        
        cost += closest_dist
        route.append(next_location)
        load.remove(next_location)
        current = next_location
        
    return route, cost



MPH = 18

def plan_truck_schedule(schedule: List[List[int]], 
                        start_time: datetime, 
                        matrix: List[List[float]]):
    routes = []
    time = start_time
    distance = float(0)
    last_location = 0
    
    while 0 < len(schedule):
        path, cost = route_load(last_location, schedule.pop(), matrix)
        routes.append(path)
        last_location = path[-1]
        distance += cost
        time += timedelta(hours = (cost / MPH))
        
    return routes, time, distance



locations, matrix, packages = get_data()

earliest_start_time = datetime.today().replace(hour = 8, 
                                      minute = 0, 
                                      second = 0, 
                                      microsecond = 0)
truck2 = [[3,23,10],[0],[17,14,7,13,1,6,19,8,12,25,2],[0],[20,21]]
route2, end_time2, miles2 = plan_truck_schedule(truck2, earliest_start_time, matrix)
print(f'\ntruck2: \n    route: {route2}\n    end_time: {end_time2}\n    miles_traveled: {miles2}\n')

later_start_time = earliest_start_time.replace(hour=9, minute=5)
truck1_locations = [[24,26,22,4,11,5,18,15,9]]
route1, end_time1, miles1 = plan_truck_schedule(truck1_locations, later_start_time, matrix)
print(f'\ntruck1: \n    route: {route1}\n    end_time: {end_time1}\n    miles_traveled: {miles1}\n')

print(f'\ntotals: \n    end_time: {max(end_time1, end_time2)}\n    miles_traveled: {miles1 + miles2}\n')

'''
    [[0, 20, 21, 24, 26, 22, 17, 4, 11, 5, 18, 15, 14, 13, 7, 1, 6, 19, 8, 12, 25, 2, 9, 3, 23, 10]]
    2023-10-28 10:39:20
    47.8
'''
