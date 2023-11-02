import csv
from typing import List
from datetime import datetime, date, time
from globals import END_OF_DAY, START_OF_DAY, TODAY
from hash_table import Dictionary
from models import Location, Package, DeliveryStatus, PackageTimeline



def __build_locations(line: List[str]):
    '''Builds a hash table of locations from the first row of the distances csv file O(n)

    Args:
        line: The first row of the distances csv file
    Returns:
        locations: The locations parsed from the csv file

    '''
    locations = Dictionary[int, Location]()

    # Enumerate location headers to create ids.
    # Skip first two columns that are not locations.
    for i, header in enumerate(line, -2):
        if i < 0:
            continue

        # Separate location name from it's address.
        values = header.split("\n")

        # Remove white space and trailing commas.
        name = values[0].strip()
        address = values[1].replace(",", "").strip()

        if i == 0:
            city_state_zip = values[2].split(",")
            state_zip = city_state_zip[1].strip().split(" ")
            locations[i] = Location(
                i,
                name,
                address,
                city=city_state_zip[0],
                state=state_zip[0],
                postal_code=state_zip[1],
                package_ids=[],
                earliest=START_OF_DAY,
                latest=END_OF_DAY,
                truck_id=None,
            )
            continue

        # Add new location to our hashmap.
        locations[i] = Location(
            i,
            name,
            address,
            city=None,
            state=None,
            postal_code=None,
            earliest=START_OF_DAY,
            latest=END_OF_DAY,
            package_ids=[],
        )
    return locations



def __get_locations():
    '''Reads data from the distances csv file then returns a hash table of locations and a matrix of distances O(n)

    Returns:
        locations: The locations parsed from the csv file
        matrix: The matrix of distances between locations

    '''

    # Instantiate return objects in outer method scope.
    locations = None
    matrix: List[List[float]] = []

    with open("distances.csv", mode="r") as file:
        lines = csv.reader(file)

        # Enumerate rows to map row/location ids.
        for i, line in enumerate(lines, -1):
            # If it's the header row, build the locations hashmap.
            if i < 0:
                locations = __build_locations(line)
                continue

            # Instantiate matrix row.
            row = []

            # Enumerate columns to map column/index location ids in row.
            # again skip label columns
            for location_id, distance_str in enumerate(line, -2):
                if location_id < 0:
                    continue

                # TODO Handle distance CSV tables whose row and column
                #      labels/indexes are not sorted.

                # If distance is for the same location,
                # replace 0 with inf to make comparing nearest neighbor easier and cleaner.
                elif i == location_id:
                    row.append(float("inf"))
                    # Break out of for loop on this last filled element to reduce cycles.
                    break

                # Otherwise, add the parsed distance to the row at the index of the column.
                distance = float(distance_str)
                row.append(distance)

                # Also add the distance to the mirrored coordinates to make it
                # easier to access the distance from either location_id.
                matrix[location_id].append(distance)

            matrix.append(row)
    return locations, matrix



def __strp_deadline(value: str):
    '''Parses a deadline string into a datetime object O(1)
    
    Args:
        value: The deadline string to parse
    Returns:
        deadline: The parsed deadline

    '''
    # Default deadline to eod.
    deadline = END_OF_DAY

    # If value is valid and not EOD, parse time and combine with today's date.
    if value.strip() and value != "EOD":
        deadline_time = datetime.strptime(value, "%I:%M %p")
        deadline = datetime.combine(TODAY, deadline_time.time())

    return deadline



def __add_packages_to_locations(locations: Dictionary[int, Location]): 
    '''Reads data from the packages csv file then adds packages to their respective locations O(n)*O(n) 

    Args:
        locations: The locations to add packages to
    Returns:
        packages: The packages parsed from the csv file
        locations: The locations that were updated with packages

    ''' 
    # TODO Make locations immutable
    # Create hashmap to hold packages.
    packages = Dictionary[int, Package]()

    with open("packages.csv") as csv_file:
        # Skip headers because we can't use labels without dictReader.
        next(csv_file)

        reader = csv.reader(csv_file)
        for line in reader:
            # Create location details that can be overridden in special cases
            package_id = int(line[0])
            address = str(line[1])
            city = line[2]
            state = line[3]
            postal_code = line[4]
            earliest = START_OF_DAY
            latest = __strp_deadline(line[5])
            at_hub_time = earliest

            # Override incorrect address details to correct ones
            # and delay the package.
            if package_id == 9:
                address = "410 S State St"
                city = "Salt Lake City"
                state = "UT"
                postal_code = "84111"
                earliest = datetime.combine(TODAY.date(), time(10, 20))

            # Find matching location for address
            for location in locations.values:
                if address == location.address:
                    package = Package(
                        package_id = package_id,
                        location_id = location.location_id,
                        weight = line[6],
                        notes = line[7],
                        earliest = earliest,
                        latest = latest,
                        timeline = PackageTimeline(at_hub_time, None, None),
                    )
                    packages[package.package_id] = package

                    # Set location address details.
                    # TODO Handle locations with the same address but different
                    #      cities, states, or zip codes.

                    location.package_ids.append(package.package_id)

                    if not location.city and city:
                        location.city = city

                    if not location.state and state:
                        location.state = state

                    if not location.postal_code and postal_code:
                        location.postal_code = postal_code

                    if package.earliest > location.earliest:
                        location.earliest = package.earliest

                    if package.latest < location.latest:
                        location.latest = package.latest

                    # Since we found a matching location,
                    # we don't need to continue through the rest.
                    # TODO Handle duplicate locations
                    break
    return packages, locations



def get_data():
    '''Reads data from the csv files then returns the locations, distance matrix, and packages O(1)

    Returns:
        locations: The locations parsed from the csv file
        matrix: The matrix of distances between locations
        packages: The packages parsed from the csv file

    '''
    locations, matrix = __get_locations()

    packages, locations = __add_packages_to_locations(locations)

    return locations, matrix, packages
