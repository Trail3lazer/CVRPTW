from datetime import datetime, timedelta
from typing import List
from globals import INCORRECT_ADDRESS_UPDATE_TIME, MPH, START_OF_DAY
from logger import (
    log_line,
    log_event,
    log,
    print_package_table,
    print_packages_at_time,
    print_route_distances_and_times,
)
from models import DeliveryStatus, Location, PackageUpdate, Stop, StopReason
from datalayer import get_data

locations, matrix, packages = get_data()
global updated_package_9_address 
updated_package_9_address = False


def update_packages(
    status: DeliveryStatus,
    location: Location,
    timestamp: datetime,
    truck_id: int,
):
    """Updates the status of a list of packages O(n)

    Args:
        status: status to set the packages to
        location: location object
        package_ids: list of package ids
        timestamp: datetime of the event
        truck_id: id of the truck
    Returns:
        package_ids: list of package ids

    """
    for p_id in location.package_ids:
        package = packages[p_id][-1].package.copy()
        package.status = status
        packages[p_id].append(PackageUpdate(timestamp, package))

        log(location, package, timestamp, truck_id)
    return location.package_ids


def calculate_truck_load(truck_load: List[int]):
    """Calculates the number of packages on a truck O(n)

    Args:
        truck_load: list of location ids
    Returns:
        package_count: number of packages on the truck

    """
    package_count = 0
    for l_id in truck_load:
        location = locations[l_id]
        package_count += len(location.package_ids)
    return package_count


# Determine the priority of neighbor by time
def calc_arrival(distance: float, cur_time: datetime, earliest: datetime):
    """Calculates the priority of a neighbor O(1)

    Args:
        distance: distance to the neighbor
        cur_time: current time
        earliest: earliest time the neighbor can be visited
    Returns:
        est_arrival_time: estimated arrival time

    """
    est_travel_hours = distance / MPH
    est_arrival_time = cur_time + timedelta(hours=(est_travel_hours))

    # If would arrive before min location time, set estimated arrival to location min time
    if est_arrival_time < earliest:
        est_arrival_time = earliest

    return est_arrival_time


def update_package_9_delivery(current_time: datetime, load: List[int]):
    """Updates the address of package 9 O(n)

    Args:
        load: list of location ids
    Returns:
        load: list of location ids

    """
    # Update the global variable to prevent this function from being called again.
    globals()["updated_package_9_address"] = True
    new_location = None

    # Find the location with the matching address.
    for location in locations.values:
        if location.address == "410 S State St":

            # Update the package location and location package ids.
            package = packages[9][-1].package.copy()
            package.location_id = location.location_id
            packages[9].append(PackageUpdate(current_time, package))
            location.package_ids.append(9)
            new_location = location
    
    not_in_load = len([l_id for l_id in load if l_id == new_location.location_id]) == 0
    truck_has_room = calculate_truck_load(load) < 16

    # If the new location is not in the load and the load has room, add the location with package 9 to the load.
    if(not_in_load and truck_has_room):
        load.append(new_location.location_id)
        new_location.package_ids = [9]
    
    return load


# Given an array of locations, use a hueristic algorithm to determine the path.
# This uses the greedy nearest neighbors algorithm. This is the self adjusting part of the code.
def route_load(
    start_location_id: int, start_time: datetime, truck_id: int, load: List[int]
):
    """Calculates the route for a truck. O(n^2)

    Args:
        start_location_id: the id of the location that the truck starts from (integer),
        start_time: the time the truck starts this route (datetime),
        truck_id: the id of the truck carrying the load,
        load: the list of location_ids in this truck load (Array[integer])
    Returns:
        route: list of stops
        cur_time: time the truck finishes
        total_route_distance: total distance traveled
        updated_package_9_address: whether or not package 9's address has been updated

    """

    # Set route starting values.
    current_id = start_location_id
    route: List[Stop] = []
    total_route_distance = float(0)
    cur_time = start_time

    # Repeat until load is empty
    while 0 < len(load):  # O(n*log(n))
        # Instantiate variables for comparing neighbors.
        # This is where the nearest neighbor is temporarily stored while comparing others.
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
            # this will change the nearest neighbor if a closer one is found.
            if best_time > est_arrival_time:
                closest_dist = distance
                best_time = est_arrival_time
                next_location = other

        assert next_location is not None

        total_route_distance += closest_dist
        cur_time = best_time
        current_id = next_location.location_id

        # Update package 9 address if it's after the update time and the package hasn't been updated yet.
        if(not globals()["updated_package_9_address"] and cur_time >= INCORRECT_ADDRESS_UPDATE_TIME):
            load = update_package_9_delivery(cur_time, load)

        # Set all stops to delivery except package hub
        reason = StopReason.delivery
        if next_location.location_id == 0:
            reason = StopReason.loading

        route.append(Stop(best_time, closest_dist, next_location, reason))

        # Update location packages to delivered
        update_packages(
            DeliveryStatus.delivered,
            next_location,
            cur_time,
            truck_id,
        )

        # Remove next location_id from load to reduce subsequent iterations,
        # prevent duplicate deliveries, and infinite loops.
        load.remove(next_location.location_id)  # O(n)

    return route, cur_time, total_route_distance


def update_load_status(
    start_location_id: int, start_time: datetime, truck_id: int, load: List[int]
):
    """Logs the status of a truck load O(1)

    Args:
        start_location_id: id of the starting location
        start_time: time the truck starts
        truck_id: id of the truck
        load: list of location ids

    """
    one_second_later = start_time.replace(second=start_time.second + 1)

    # If the truck is empty, log that it is heading back to the hub to reload.
    if len(load) == 1:
        log_line(one_second_later, "")
        log_event(
            one_second_later, f"Truck {truck_id} is heading back to the hub to reload."
        )
        log_line(one_second_later, "")
    # Otherwise, log the truck is loaded with the packages.
    else:
        log_line(start_time)
        log_event(
            start_time,
            f"Truck {truck_id} is loaded with these {calculate_truck_load(load)} packages.",
        )
        log_line(start_time, "")

        start_location = locations[start_location_id]

        # Update location packages to en route
        for l in sorted(load):
            loaded_location = locations[l]
            loaded_location.truck_id = truck_id
            update_packages(
                DeliveryStatus.enroute,
                loaded_location,
                start_time,
                truck_id,
            )

        log_line(one_second_later)
        log_line(one_second_later, "")


def plan_truck_schedule(truck_id: int, schedule: List[List[int]], start_time: datetime):
    """Plans the schedule for a truck O(n)

    Args:
        truck_id: id of the truck
        schedule: list of lists of location ids
        start_time: time the truck starts
    Returns:
        routes: list of lists of stops
        current_time: time the truck finishes
        distance: total distance traveled

    """
    routes = []
    current_time = start_time
    distance = float(0)
    last_location = 0

    while 0 < len(schedule):  # O(n)
        next_load = schedule.pop()
        update_load_status(last_location, current_time, truck_id, next_load)
        route, end_time, miles = route_load(
            last_location, current_time, truck_id, next_load
        )
        routes.append(route)
        last_location = route[-1].location.location_id
        distance += miles
        current_time = end_time

    return routes, current_time, distance


def main():
    """Main function O(n) Constant: time = 0.0029 (sec)"""

    later_start_time = START_OF_DAY.replace(hour=9, minute=5)
    truck1 = [[22, 24, 26], [0], [2, 4, 5, 9, 11, 14, 15, 18]]
    for location_id in truck1[-1]:
        update_packages(DeliveryStatus.hub, locations[location_id], later_start_time, 1)
    route1, t1_end, t1_miles = plan_truck_schedule(1, truck1, later_start_time)

    truck2 = [[1, 6, 7, 8, 12, 13, 19, 17, 25], [0], [3, 10, 23], [0], [20, 21]]
    route2, t2_end, t2_miles = plan_truck_schedule(2, truck2, START_OF_DAY)

    running = True
    while running:
        user_input = input(
            """Do one of the following:
            To check package status, enter a time greater than 08:00 formated as military time 'hhmm'.
            To print the delivery timeline events of all packages, enter 'T'. 
            To print the total miles traveled and time taken for all trucks, enter 'S'.
            To exit, enter 'X'. 
            :"""
        )

        if user_input.lower() == "x":
            running = False
        elif user_input.lower() == "t":
            print_package_table()
        elif user_input.lower() == "s":
            print_route_distances_and_times(t1_end, t1_miles, t2_end, t2_miles)
        else:
            input_time = None
            try:
                input_time = datetime.strptime(user_input, "%H%M")
            except ValueError:
                print(
                    f'Your input of "{user_input}" is not one of the options and is an invalid time format. \nPlease rerun the program to try again. \nExiting...'
                )
                break
            print_packages_at_time(input_time, packages, locations)

main()