import delivery
import truck

import pandas as pd
import networkx as nx

df = pd.read_excel("./WGUPS Distance Table.xlsx", header=7).drop("Unnamed: 1", axis=1)
addresses = []
edges = {}

for idx, address in enumerate(df.columns):
    # skip label column
    if idx == 0:
        continue
    i = idx-1
    addresses.append({'id': i, 'address': address})
    edges[i] = {}
    for j in range(1, i+1):
        weight = df.iat[i, j]
        print([i, j, weight])
        edges[i][j] = {'weight': weight}

print(addresses)

g = nx.Graph(edges)
