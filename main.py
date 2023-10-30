
# Studend ID: 010771776

from datetime import datetime, timedelta
from typing import List,Any
from hash_table import Dictionary
from models import DeliveryStatus, Location, Package, Stop, StopReason, strfdatetime
from datalayer import get_data

locations, matrix, packages = get_data()
start_of_day = datetime.today().replace(hour = 8, minute = 0, 
                                        second = 0, microsecond = 0)
end_of_day = start_of_day.replace(hour=17)
MPH = 18
log_obj = Dictionary[str, list[str]]()

# Scope variables that should not be global
def get_avg_distance():
    last_row = matrix[-1].copy()
    last_row.pop()
    return sum(last_row)/len(last_row)
avg_distance = get_avg_distance()



def log(location: Location, package: Package, timestamp: datetime, truck_id: int):
    message = Dictionary[str, str]()
    message["Package ID"] = package.package_id
    message["Truck ID"] = truck_id
    message["Location Name"] = location.name
    message["Location Address"] = f'{location.address}, {location.city}, {location.state} {location.postal_code}'
    message["Status"] = package.status
    log_obj[strfdatetime(timestamp)].append(str(message))



def update_packages(updates: Dictionary[str, Any], location: Location, 
                    package_ids: List[Package], timestamp: datetime, truck_id: int):
    
    for p_id in package_ids:
        package = packages[p_id]
        for e in updates.entries:
            package[e.key] = e.value
        log(location,package,timestamp, truck_id)
    return package_ids



# Determine the rank of neighbor by distance and time requirements
def calc_piority(distance: float, avg_distance: float, 
                      cur_time: datetime, earliest: datetime, latest: datetime):
    
    est_travel_hours = distance / MPH
    est_arrival_time = cur_time + timedelta(hours = (est_travel_hours))
    
    # If would arrive before min location time, set estimated arrival to location min time
    if(est_arrival_time < earliest):
        est_arrival_time = earliest
    
    travel_seconds = (est_arrival_time - cur_time).total_seconds()
    deadline_seconds = (latest - est_arrival_time).total_seconds()
    
    # Make priority a balance between delivery deadlines and travel distance.
    # Lower numbers are higher priority.
    priority = distance-(avg_distance/travel_seconds)-(avg_distance/deadline_seconds)
    
    return priority, est_arrival_time, distance
    
            

# Given an array of locations, determine K-Nearest Neighbors path
def route_load(start_location_id: int, start_time: datetime, truck_id: int, load: List[int]):
    
    # Set route starting values.
    current_id = start_location_id
    route = []
    total_route_distance = 0
    cur_time = start_time
    
    # Repeat untill load is empty
    while 0 < len(load):
        
        # Instantiate variables for comparing neighbors.
        next_location: Location = None
        highest_priority: float = float("inf")
        best_time: datetime = datetime.max
        closest_dist: float = float("inf")
        distances = matrix[current_id]
        
        # Loop through other package locations loaded on the truck.
        for other_id in load:
            assert other_id is not None
            
            other = locations[other_id]
            
            (other_priority, 
             est_arrival_time, 
             distance) = calc_piority(distances[other_id],
                                           avg_distance,
                                           cur_time,
                                           other.earliest or start_of_day, 
                                           other.latest or datetime.max)
            
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
        package_updates = Dictionary[str, Any]()
        package_updates['status'] = DeliveryStatus.delivered
        package_updates['delivery_time'] = cur_time
        
        update_packages(package_updates, next_location, 
                        next_location.package_ids, cur_time, 
                        truck_id)
        
        # Remove location_id from load to prevent infinite loop
        load.remove(next_location.location_id)
        
    return route, cur_time, total_route_distance



def plan_truck_schedule(truck_id:int, schedule: List[List[int]], start_time: datetime):
    routes = []
    time = start_time
    distance = float(0)
    last_location = 0
    
    while 0 < len(schedule):
        path, cost = route_load(last_location, start_time, truck_id, schedule.pop())
        routes.append(path)
        last_location = path[-1]
        distance += cost
        
    return routes, time, distance



truck2 = [[3,23,10],[0],[17,14,7,13,1,6,19,8,12,25,2],[0],[20,21]]
route2, end_time2, miles2 = plan_truck_schedule(2, truck2, start_of_day)
print(f'\ntruck2: \n    route: {route2}\n    end_time: {end_time2}\n    miles_traveled: {miles2}\n')

later_start_time = start_of_day.replace(hour=9, minute=5)
truck1_locations = [[24,26,22,4,11,5,18,15,9]]
route1, end_time1, miles1 = plan_truck_schedule(truck1_locations, later_start_time)
print(f'\ntruck1: \n    route: {route1}\n    end_time: {end_time1}\n    miles_traveled: {miles1}\n')

print(f'\ntotals: \n    end_time: {max(end_time1, end_time2)}\n    miles_traveled: {miles1 + miles2}\n')
