from datetime import datetime, timedelta
from math import floor
from random import random
import time
from typing import Any, List
from globals import MPH, START_OF_DAY
from models import DeliveryStatus, Location, Package, Stop, StopReason, strfdatetime
from datalayer import get_data

locations, matrix, packages = get_data()
log_obj = []



def build_format_str(cols: List[int]):
    '''Builds a format string for use with str.format() O(n)

    Args:
        cols: list of column widths
    Returns:
        format_str: string with format specifiers for each column

    '''
    format_str = ""
    for c in cols:
        format_str += f"{{:<{c}}}   "
    return format_str



def log_event(timestamp: datetime, message: str):
    '''Adds an event to the log object O(1)

    Args:
        timestamp: datetime of the event
        message: string describing the event

    '''
    time_str = strfdatetime(timestamp)
    log_obj.append([time_str, "", message])



def log_line(timestamp: datetime, char: str = "—"):
    '''Adds a line to the log object O(1)

    Args:
        timestamp: datetime of the event
        char: character to use for the line

    '''
    log_event(timestamp, 200*char)



def create_status_description(current_time: datetime, package: Package):
    '''Creates a string describing the status of a package O(1)

    Args:
        current_time: the current time
        package: the package to get the status of
    Returns:
        status: string describing the status of the package

    '''

    timeline = package.timeline
    if timeline.delivered != None and timeline.delivered <= current_time:
        return f"Delivered at {strfdatetime(timeline.delivered)}"
    elif timeline.enroute != None and timeline.enroute <= current_time:
        return f"Enroute at {strfdatetime(timeline.enroute)}"
    elif timeline.at_hub <= current_time:
        return "At hub"
    return "Awaiting arrival at hub"



log_msg_format = build_format_str([25, 8, 16, 5, 6, 21, 6])
def create_package_log_message(location: Location, package: Package, timestamp: datetime, truck_id: int):
    '''Creates a string describing the status of a package O(1)
    
    Args:
        location: location object
        package: package object
        timestamp: datetime of the event
        truck_id: id of the truck
    Returns:
        message: string describing the status of the package

    '''
    status = create_status_description(timestamp, package)
    deadline = strfdatetime(package.latest)
    message = log_msg_format.format(*[location.address, deadline, location.city, location.postal_code, package.weight, status, str(truck_id)])
    return message



def log(location: Location, package: Package, timestamp: datetime, truck_id: int):
    '''Adds a package status updates to the log object O(n)

    Args:
        location: location object
        package: package object
        timestamp: datetime of the event
        truck_id: id of the truck

    '''
    message = create_package_log_message(location, package, timestamp, truck_id)
    log_obj.append([strfdatetime(timestamp), package.package_id, message])



def update_packages(
    status: str,
    location: Location,
    package_ids: List[int],
    timestamp: datetime,
    truck_id: int,
):
    '''Updates the status of a list of packages O(n)

    Args:
        status: status to set the packages to
        location: location object
        package_ids: list of package ids
        timestamp: datetime of the event
        truck_id: id of the truck
    Returns:
        package_ids: list of package ids

    '''
    for p_id in package_ids:
        package = packages[p_id]
        if status == DeliveryStatus.enroute:
            package.timeline.enroute = timestamp
        elif status == DeliveryStatus.delivered:
            package.timeline.delivered = timestamp
            
        log(location, package, timestamp, truck_id)
    return package_ids



def calculate_truck_load(truck_load: List[int]):
    '''Calculates the number of packages on a truck O(n)

    Args:
        truck_load: list of location ids
    Returns:
        package_count: number of packages on the truck

    '''
    package_count = 0
    for l_id in truck_load:
        location = locations[l_id]
        package_count += len(location.package_ids)
    return package_count



# Determine the priority of neighbor by time
def calc_arrival(distance: float, cur_time: datetime, earliest: datetime):
    '''Calculates the priority of a neighbor O(1)

    Args:
        distance: distance to the neighbor
        cur_time: current time
        earliest: earliest time the neighbor can be visited
    Returns:
        est_arrival_time: estimated arrival time

    '''
    est_travel_hours = distance / MPH
    est_arrival_time = cur_time + timedelta(hours=(est_travel_hours))

    # If would arrive before min location time, set estimated delivery to location min time
    if est_arrival_time < earliest:
        est_arrival_time = earliest

    return est_arrival_time



# Given an array of locations, determine K-Nearest Neighbors path
def route_load(start_location_id: int, start_time: datetime, truck_id: int, load: List[int]):
    '''Calculates the route for a truck O(n*log(n))

    Args:
        start_location_id: id of the starting location
        start_time: time the truck starts
        truck_id: id of the truck
        load: list of location ids
    Returns:
        route: list of stops
        cur_time: time the truck finishes
        total_route_distance: total distance traveled

    '''
    # Set route starting values.
    current_id = start_location_id
    route: List[Stop] = []
    total_route_distance = float(0)
    cur_time = start_time

    # Repeat until load is empty
    while 0 < len(load): # O(n*log(n))
        # Instantiate variables for comparing neighbors.
        next_location: Location = None
        best_time: datetime = datetime.max
        closest_dist: float = float("inf")

        # Loop through other package locations loaded on the truck.
        for other_id in load:
            if other_id == current_id:
                continue

            distance = matrix[current_id][other_id]
            other = locations[other_id]

            # Calculate the estimated arrival time.
            est_arrival_time = calc_arrival(       
                distance, cur_time, other.earliest or START_OF_DAY
            )

            # find the highest priority (min) by comparing each item in the load.
            if best_time > est_arrival_time:
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
        update_packages(
            DeliveryStatus.delivered,
            next_location,
            next_location.package_ids,
            cur_time,
            truck_id,
        )

        # Remove next location_id from load to reduce subsequent iterations, 
        # prevent duplicate deliveries, and infinite loops.
        load.remove(next_location.location_id) # O(n)

    return route, cur_time, total_route_distance



def log_load_status(start_location_id: int, start_time: datetime, truck_id: int, load: List[int]):
    '''Logs the status of a truck load O(n)

    Args:
        start_location_id: id of the starting location
        start_time: time the truck starts
        truck_id: id of the truck
        load: list of location ids

    '''
    one_second_later = start_time.replace(second=start_time.second+1)

    # If the truck is empty, log that it is heading back to the hub to reload.
    if len(load) == 1:
        log_line(one_second_later, "")
        log_event(
            one_second_later, f"Truck {truck_id} is heading back to the hub to reload.")
        log_line(one_second_later, "")
    # Otherwise, log the truck is loaded with the packages.
    else:
        log_line(start_time)
        log_event(
            start_time, f"Truck {truck_id} is loaded with these {calculate_truck_load(load)} packages.")
        log_line(start_time, "")

        start_location = locations[start_location_id]

        # Update location packages to en route
        for l in sorted(load):
            loaded_location = locations[l]
            loaded_location.truck_id = truck_id
            update_packages(
                DeliveryStatus.enroute,
                start_location,
                loaded_location.package_ids,
                start_time,
                truck_id,
            )

        log_line(one_second_later)
        log_line(one_second_later, "")



def plan_truck_schedule(truck_id: int, schedule: List[List[int]], start_time: datetime):
    '''Plans the schedule for a truck O(n)

    Args:
        truck_id: id of the truck
        schedule: list of lists of location ids
        start_time: time the truck starts
    Returns:
        routes: list of lists of stops
        current_time: time the truck finishes
        distance: total distance traveled

    '''
    routes = []
    current_time = start_time
    distance = float(0)
    last_location = 0

    while 0 < len(schedule): # O(n)
        next_load = schedule.pop()
        log_load_status(last_location, current_time, truck_id, next_load)
        route, end_time, miles = route_load(
            last_location, current_time, truck_id, next_load
        )
        routes.append(route)
        last_location = route[-1].location.location_id
        distance += miles
        current_time = end_time

    return routes, current_time, distance



def print_package_table(print_list: List[List[Any]]):
    '''Prints the log as a table O(n)
    
    Args:
        print_list: list of lists to print as a table
    
    '''
    
    def sort_key(s):
        pkg_time = datetime.strptime(s[0], "%H:%M:%S")
        try:
            pkg_time.replace(microsecond=s[1])
        except:
            pass
        return pkg_time

    sorted_list = sorted(print_list, key=sort_key)
    headers_format = build_format_str([9, 2])+log_msg_format

    log_headers = ["Timestamp", "ID", "Address", "Deadline", "City", "Zip", "Weight", "Status", "Truck"]

    print(headers_format.format(*log_headers))

    log_row_format = build_format_str([9, 2, 150])
    for row in sorted_list: # O(n)
        print(log_row_format.format(*row))



def print_route_distances_and_times(end_time1,miles1,end_time2,miles2):
    '''Prints the route distances and times O(1)'''
    
    print(f"truck1:\n    end_time: {end_time1}\n    miles_traveled: {miles1}\n")
    print(f"truck2:\n    end_time: {end_time2}\n    miles_traveled: {miles2}\n")
    print(f"totals:\n    end_time: {max(end_time1, end_time2)}\n    miles_traveled: {miles1 + miles2}\n")



def print_packages_at_time(current_time: datetime):
    '''Prints the status of all packages at a given time O(n)
    
    Args:
        current_time: time to check the status of the packages
        
    '''
    # Change the input time to the current day to prevent incorrect comparisons with package updates.
    cleaned_time = START_OF_DAY.replace(hour=current_time.hour, minute=current_time.minute, second=current_time.second)
    package_rows = []

    # Sort the packages by id to ensure they are printed in order.
    for p in sorted(packages.values, key= lambda p: p.package_id):
        location = locations[p.location_id]
        row = create_package_log_message(location, p, cleaned_time, location.truck_id)
        package_rows.append([strfdatetime(cleaned_time), p.package_id, row])
    print_package_table(package_rows)



def main():
    '''Main function O(n)'''

    later_start_time = START_OF_DAY.replace(hour=9, minute=5)
    truck1 = [[24, 26, 22], [0], [4, 14, 11, 5, 18, 15, 9, 2]]
    route1, t1_end, t1_miles = plan_truck_schedule(1, truck1, later_start_time)

    truck2 = [[17, 7, 13, 1, 6, 19, 8, 12, 25], [0], [3, 23, 10], [0], [20, 21]]
    route2, t2_end, t2_miles = plan_truck_schedule(2, truck2, START_OF_DAY)

    running = True
    while running:
        user_input = input('''Do one of the following:
            To check package status, enter a time greater than 08:00 formated as military time 'hhmm'.
            To print the delivery timeline events of all packages, enter 'T'. 
            To print the total miles traveled and time taken for all trucks, enter 'S'.
            To exit, enter 'X'. 
            :''')
        if user_input.lower() == "x":
            running = False
            continue
        elif user_input.lower() == "t":
            print_package_table(log_obj)
            continue
        elif user_input.lower() == "s":
            print_route_distances_and_times(t1_end,t1_miles,t2_end,t2_miles)
            continue
        
        input_time = None
        try:
            input_time = datetime.strptime(user_input, "%H%M")
        except ValueError:
            print(f'Your input of "{user_input}" is not one of the options and is an invalid time format. \nPlease rerun the program to try again. \nExiting...')
            break
        
        print_packages_at_time(input_time)
            

main()