import delivery
import truck
import dictionary
import csv
 
addresses = []
edges = {}

def main(df: csv.DictReader[str]):
    for idx, address in enumerate(df.fieldnames):
        # skip label column
        if idx == 0:
            continue
        i = idx-1
        addresses.append({'id': i, 'address': address})
        edges[i] = {}
        for j in range(1, i+1):
            weight = df[i][j]
            print([i, j, weight])
            edges[i][j] = weight

    print(addresses)

    print 

# opening the CSV file
with open("distance_table.csv", mode ='r') as file:    
    # reading the CSV file
    df = csv.DictReader(file)
    main(df)
