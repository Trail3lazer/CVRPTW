from datetime import datetime
from typing import Any, List
from globals import START_OF_DAY
from hash_table import Dictionary
from models import Location, Package, strfdatetime


event_log = []

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
    event_log.append([time_str, "", message])



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
    # If the package has been delivered, return the delivery time.
    if timeline.delivered != None and timeline.delivered <= current_time:
        return f"Delivered at {strfdatetime(timeline.delivered)}"
    
    # If the package is enroute, return the enroute time.
    elif timeline.enroute != None and timeline.enroute <= current_time:
        return f"Enroute at {strfdatetime(timeline.enroute)}"
    
    # If the package is at the hub, return at hub.
    elif timeline.at_hub <= current_time:
        return "At hub"
    
    # Otherwise, package has not arrived at the hub yet.
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
    event_log.append([strfdatetime(timestamp), package.package_id, message])



def print_package_table():
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

    sorted_list = sorted(event_log, key=sort_key)
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



def print_packages_at_time(current_time: datetime, packages: Dictionary[int, Package], locations: Dictionary[int, Location]):
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
