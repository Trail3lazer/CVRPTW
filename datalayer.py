from typing import List
from datetime import datetime
import csv
from hash_table import Dictionary
from models import Location, Package, DeliveryStatus

def _make_location_lookup(line: List[str]):
    end_of_day = datetime.today().replace(hour = 17)
    locations = Dictionary[int, Location]()
    for i, header in enumerate(line, -2):
        if i < 0: continue
        values = header.split('\n')
        print(values)
        name = values[0].strip()
        address = values[1].replace(",", "").strip()
        locations[i] = Location(i, name, address, 
                                status=DeliveryStatus.at_hub,
                                deadline=end_of_day
                                stop_number=None, 
                                truck=None,
                                package_ids=[])
    return locations

def get_locations():
    locations = None
    matrix: List[List[float]] = []
    with open("distances.csv", mode ='r') as file:
        lines = csv.reader(file)
        for i,line in enumerate(lines, -1):
            if i < 0:
                locations = _make_location_lookup(line)
                continue
            line_weights = []
            for address_id, weight_str in enumerate(line, -2):
                if address_id < 0: 
                    continue
                elif i == address_id: 
                    line_weights.append(float("inf"))
                    break
                else:
                    weight = float(weight_str)
                    line_weights.append(weight)
                    matrix[address_id].append(weight)
            matrix.append(line_weights)
    return locations, matrix


def get_package_lookup(locations: Dictionary[int, Location]):
    
    end_of_day = datetime.today().replace(hour = 17)
    def datetimefstr(value: str):
        if not value.strip() or value == "EOD":
            return None
        return datetime.strptime(value, "%i:%M %p")
    
    location_list = locations.values
    packages = Dictionary[int, Package]()
    with open("packages.csv") as csv_file:
        next(csv_file) # skip headers because we can't use dictReader.
        lines = csv.reader(csv_file)
        for line in lines:
            deadline=datetimefstr(line[5])
            for location in location_list:
                if line[1] == location.address:
                    package = Package(
                                package_id = int(line[0]), 
                                location_id = location.location_id, 
                                address = line[1], 
                                city = line[2], 
                                state = line[3], 
                                postal_code = line[4],
                                package_weight=line[6], 
                                notes=line[7])
                    packages[package.package_id] = package
                    location.package_ids.append(package.package_id)
                    if deadline and deadline < location.deadline:
                        location.deadline = deadline
                    break
    return packages
