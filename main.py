
# Studend ID: 010771776

from datetime import datetime, timedelta
import json
from typing import List,Any
from globals import END_OF_DAY, MPH, SECONDS_IN_DAY, START_OF_DAY
from hash_table import Dictionary
from models import DeliveryStatus, Location, Package, Stop, StopReason, strfdatetime
from datalayer import get_data

locations, matrix, packages = get_data()
log_obj: dict[str, list[str]] = {}

# print(packages)

def log(location: Location, package: Package, timestamp: datetime, truck_id: int):
    message = {
        "Package ID":package.package_id, 
        "Truck ID": truck_id,
        "Status": package.status,
        "Location Name": location.name,
        "Location Address": f'{location.address}, {location.city}, {location.state} {location.postal_code}'
    }
    key = strfdatetime(timestamp)
    time_logs = None
    if key in log_obj.keys():
        time_logs = log_obj[key]
    else:
        time_logs = []
        log_obj[key] = time_logs
    time_logs.append(str(message))



def update_packages(status: str, location: Location, 
                    package_ids: List[int], timestamp: datetime, truck_id: int):
    
    for p_id in package_ids:
        package = packages[p_id]
        if status == DeliveryStatus.delivered:
            package.delivery_time = timestamp
        package.status = status
        log(location,package,timestamp, truck_id)
    return package_ids



# Determine the priority of neighbor by distance and time requirements
def calc_piority(distance: float, cur_time: datetime, earliest: datetime, latest: datetime):
    
    est_travel_hours = distance / MPH
    est_arrival_time = cur_time + timedelta(hours = (est_travel_hours))
    est_delivery = est_arrival_time
    
    # If would arrive before min location time, set estimated delivery to location min time
    if(est_delivery < earliest):
        est_delivery = earliest
    
    travel = (est_arrival_time - cur_time).total_seconds()
    delivery = (est_delivery - cur_time).total_seconds()-travel
    deadline = (latest - cur_time).total_seconds()-travel
    
    # Make priority a balance between delivery deadlines, delays and travel time/distance.
    # Lower numbers are higher priority.
    priority = (delivery+deadline) / travel
    
    return priority, est_delivery
    
            

# Given an array of locations, determine K-Nearest Neighbors path
def route_load(start_location_id: int, start_time: datetime, truck_id: int, load: List[int]):
    
    start_location = locations[start_location_id]
    for l in sorted(load):
        loaded_location = locations[l]
        update_packages(DeliveryStatus.en_route, start_location, 
                        loaded_location.package_ids, start_time, 
                        truck_id)
    
    # Set route starting values.
    current_id = start_location_id
    route: List[Stop] = []
    total_route_distance = float(0)
    cur_time = start_time
    
    # Repeat untill load is empty
    while 0 < len(load):
        
        # Instantiate variables for comparing neighbors.
        next_location: Location = None
        highest_priority: float = float("inf")
        best_time: datetime = datetime.max
        closest_dist: float = float("inf")
        
        # Loop through other package locations loaded on the truck.
        for other_id in load:
            if(other_id == current_id): continue
            
            other = locations[other_id]
            distance = matrix[current_id][other_id]
            (other_priority, 
             est_arrival_time) = calc_piority(distance,
                                           cur_time,
                                           other.earliest or START_OF_DAY, 
                                           other.latest or END_OF_DAY)
            
            # find the highest priority (min) by comparing each item in the load.
            if other_priority < highest_priority:
                highest_priority = other_priority
                closest_dist = distance
                best_time = est_arrival_time
                next_location = other
        
        assert next_location is not None
        
        total_route_distance += closest_dist
        cur_time = best_time
        current_id = next_location.location_id
        
        # Set all stops to delivery except package hub
        reason = StopReason.delivery
        if next_location.location_id == 0:
            reason = StopReason.loading
            
        route.append(Stop(best_time, closest_dist, next_location, reason))
        
        # Update location packages to delivered
        update_packages(DeliveryStatus.delivered, next_location, 
                        next_location.package_ids, cur_time, 
                        truck_id)
        
        # Remove location_id from load to prevent infinite loop
        load.remove(next_location.location_id)
        
    return route, cur_time, total_route_distance



def plan_truck_schedule(truck_id:int, schedule: List[List[int]], start_time: datetime):
    routes = []
    current_time = start_time
    distance = float(0)
    last_location = 0
    
    while 0 < len(schedule):
        route, end_time, miles = route_load(last_location, start_time, truck_id, schedule.pop())
        routes.append(route)
        last_location = route[-1].location.location_id
        distance += miles
        current_time = end_time
        
    return routes, current_time, distance



truck2 = [[i for i in range(21)]] #[[3,23,10],[0],[17,14,7,13,1,6,19,8,12,25,2],[0],[20,21]]
route2, end_time2, miles2 = plan_truck_schedule(2, truck2, START_OF_DAY)
route = json.dumps(log_obj, indent=2)
print(f'\ntruck2: \n    route: {route}\n    end_time: {end_time2}\n    miles_traveled: {miles2}\n')

'''
later_start_time = START_OF_DAY.replace(hour=9, minute=5)
truck1_locations = [[24,26,22,4,11,5,18,15,9]]
route1, end_time1, miles1 = plan_truck_schedule(1, truck1_locations, later_start_time)
print(f'\ntruck1: \n    route: {route1}\n    end_time: {end_time1}\n    miles_traveled: {miles1}\n')

print(f'\ntotals: \n    end_time: {max(end_time1, end_time2)}\n    miles_traveled: {miles1 + miles2}\n')
'''