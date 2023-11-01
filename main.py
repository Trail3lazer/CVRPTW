# Studend ID: 010771776

from datetime import datetime, timedelta
import json
from math import floor
from random import random
from typing import List
from globals import MPH, START_OF_DAY
from models import DeliveryStatus, Location, Package, Stop, StopReason, strfdatetime
from datalayer import get_data

locations, matrix, packages = get_data()


def build_format_str(cols: List[int]):
    format_str = ""
    for c in cols:
        format_str += f"{{:<{c}}}   "
    return format_str


log_obj = []
log_msg_format = build_format_str([9, 8, 3, 7, 42, 49, 100])

# print(packages)


def log_event(timestamp: datetime, message: str):
    time_str = strfdatetime(timestamp)
    log_obj.append([time_str, "", message])


def log_line(timestamp: datetime, char: str = "—"):
    log_event(timestamp, 200*char)


def log(location: Location, package: Package, timestamp: datetime, truck_id: int):
    message = [package.status, strfdatetime(package.latest), location.location_id, truck_id, location.name,
               f'{location.address}, {location.city}, {location.state} {location.postal_code}', package.notes]

    log_obj.append([strfdatetime(timestamp), package.package_id,
                   log_msg_format.format(*message)])


def update_packages(
    status: str,
    location: Location,
    package_ids: List[int],
    timestamp: datetime,
    truck_id: int,
):
    for p_id in package_ids:
        package = packages[p_id]
        if status == DeliveryStatus.delivered:
            package.delivery_time = timestamp
        package.status = status
        log(location, package, timestamp, truck_id)
    return package_ids


def calculate_truck_load(truck_load: List[int]):
    package_count = 0
    for l_id in truck_load:
        location = locations[l_id]
        package_count += len(location.package_ids)
    return package_count


# Determine the priority of neighbor by time
def calc_piority(distance: float, cur_time: datetime, earliest: datetime):
    est_travel_hours = distance / MPH
    est_arrival_time = cur_time + timedelta(hours=(est_travel_hours))

    # If would arrive before min location time, set estimated delivery to location min time
    if est_arrival_time < earliest:
        est_arrival_time = earliest

    return est_arrival_time


# Given an array of locations, determine K-Nearest Neighbors path
def route_load(start_location_id: int, start_time: datetime, truck_id: int, load: List[int]):

    # Set route starting values.
    current_id = start_location_id
    route: List[Stop] = []
    total_route_distance = float(0)
    cur_time = start_time

    # Repeat untill load is empty
    while 0 < len(load):
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

            est_arrival_time = calc_piority(
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
        # Remove location_id from load to prevent infinite loop
        load.remove(next_location.location_id)

    return route, cur_time, total_route_distance


def log_load_status(start_location_id: int, start_time: datetime, truck_id: int, load: List[int]):
    one_second_later = start_time.replace(second=start_time.second+1)
    if len(load) == 1:
        log_line(one_second_later, "")
        log_event(
            one_second_later, f"Truck {truck_id} is heading back to the hub to reload.")
        log_line(one_second_later, "")
    else:
        log_line(start_time)
        log_event(
            start_time, f"Truck {truck_id} is loaded with these {calculate_truck_load(load)} packages.")

        start_location = locations[start_location_id]
        for l in sorted(load):
            loaded_location = locations[l]
            update_packages(
                DeliveryStatus.en_route,
                start_location,
                loaded_location.package_ids,
                start_time,
                truck_id,
            )

        log_line(one_second_later)


def plan_truck_schedule(truck_id: int, schedule: List[List[int]], start_time: datetime):
    routes = []
    current_time = start_time
    distance = float(0)
    last_location = 0

    while 0 < len(schedule):
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


def calc_route_distance(routes: List[List[Stop]]):
    total = float(0)
    for r in routes:
        for stop in r:
            total += stop.travel_distance
    return total


def rand_in_range(start: int, end: int):
    diff = end - start
    return floor(diff * random()) + start


truck2 = [[17, 7, 13, 1, 6, 19, 8, 12, 25], [0], [3, 23, 10], [0], [20, 21]]


route2, end_time2, miles2 = plan_truck_schedule(2, truck2, START_OF_DAY)

later_start_time = START_OF_DAY.replace(hour=9, minute=5)
truck1 = [[24, 26, 22], [0], [4, 14, 11, 5, 18, 15, 9, 2]]
route1, end_time1, miles1 = plan_truck_schedule(1, truck1, later_start_time)

#
# print(json.dumps(log_obj, indent=2, sort_keys=True))
sorted_log = sorted(log_obj, key=lambda s: f'{s[0]} {s[1]}')
headers_format = build_format_str([9, 2, 9, 8, 3, 7, 42, 49, 100])

log_headers = ["Timestamp", "ID", "Status", "Deadline",
               "LID", "TruckId", "Name", "Address", "Notes"]
print(headers_format.format(*log_headers))

log_row_format = build_format_str([9, 2, 255])
for row in sorted_log:
    print(log_row_format.format(*row))


print(f"\ntruck1: \n   end_time: {end_time1}\n    miles_traveled: {miles1}\n")

print(f"\ntruck2: \n   end_time: {end_time2}\n    miles_traveled: {miles2}\n")

print(
    f"\ntotals: \n    end_time: {max(end_time1, end_time2)}\n    miles_traveled: {miles1 + miles2}\n"
)
