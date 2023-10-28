from typing import List
from datetime import datetime, date, time
import csv
from hash_table import Dictionary
from models import Location, Package, DeliveryStatus



# Extracted logic from get_locations to reduce nesting
def __build_locations(line: List[str]):
    locations = Dictionary[int, Location]()
    
    # Enumerate location headers to create ids.
    # Skip first two columns that are not locations.
    for i, header in enumerate(line, -2):
        if i < 0: continue
        
        # Separate location name from it's address. 
        values = header.split('\n')
        
        # Remove white space and trailing commas.
        name = values[0].strip()
        address = values[1].replace(",", "").strip()
        
        # Add new location to our hashmap.
        locations[i] = Location(i, name, address, 
                                city = None, 
                                state = None, 
                                postal_code = None,
                                status = DeliveryStatus.at_hub,
                                deadline = None,
                                delivery_time = None,
                                stop_number = None, 
                                truck = None,
                                package_ids = [])
    return locations



def __get_locations():
    
    # Instantiate return objects in outer method scope.
    locations = None
    matrix: List[List[float]] = []
    
    with open("distances.csv", mode ='r') as file:
        lines = csv.reader(file)
        
        # Enumerate rows to map row/location ids.
        for i,line in enumerate(lines, -1):
            
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



# Extracted logic from __add_packages to reduce nesting and redundancy
def __strp_deadline(value: str, today: date, eod: time):
    
    # Default deadline to eod.
    deadline = datetime.combine(today, eod)
    
    # If value is valid and not EOD, parse time and combine with today's date.
    if value.strip() and value != "EOD":
        deadline_time = datetime.strptime(value, "%I:%M %p")
        deadline=datetime.combine(today, deadline_time.time())
        
    return deadline



# Extracted logic from __add_packages to reduce nesting
def __build_package(location_id: int, line: List[str]):
    return Package(
                package_id = int(line[0]), 
                location_id = location_id, 
                package_weight = line[6], 
                notes = line[7])



def __add_packages_to_locations(locations: Dictionary[int, Location]):
    # Respecting immutable parameters
    updated_locations = Dictionary[int, Location]()
    
    # Create static variables outside the loop to reduce operations.
    today = date.today() 
    eod = time(17,0)
    
    # Create hashmap to hold packages.
    packages = Dictionary[int, Package]()
    
    with open("packages.csv") as csv_file:
        # Skip headers because we can't use labels without dictReader.
        next(csv_file) 
        
        reader = csv.reader(csv_file)
        for line in reader:
            address = str(line[1])
            for location in locations.values:
                if address == location.address:
                    package = __build_package(location.location_id, line)
                    packages[package.package_id] = package
                    
                    #TODO Make locations immutable
                    location.package_ids.append(package.package_id)
                    
                    # Update location deadline if package has earlier delivery deadline.
                    deadline = __strp_deadline(line[5], today, eod)
                    if not location.deadline or deadline < location.deadline:
                        location.deadline = deadline
                    
                    city = line[2]
                    state = line[3]
                    postal_code = line[4]
                    
                    # Set location address details if they are not already set.
                    # TODO Handle locations with the same address but different 
                    #      cities, states, or postal_codes.
                    if not location.city and city:
                        location.city = city
                    
                    if not location.state and state:
                        location.state = state
                        
                    if not location.postal_code and postal_code:
                        location.postal_code = postal_code
                    
                    # Add copied location to copied hashmap
                    updated_locations[location.location_id] = location
                    
                    # Since we found a matching location, 
                    # we don't need to continue through the rest. 
                    # TODO Handle duplicate locations
                    break
    return packages, updated_locations



# Wraps the file's method flow and the returns results.
def get_data():
    locations, matrix = __get_locations()
    
    packages, locations = __add_packages_to_locations(locations)
    
    return locations, matrix, packages