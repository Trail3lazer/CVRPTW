import pandas as pd

df = pd.read_excel("./WGUPS Distance Table.xlsx", header=7).drop("Unnamed: 1", axis=1)
print(df.to_string())
addresses = df["DISTANCE BETWEEN HUBS IN MILES"]
print(addresses.to_string())
df.columns=[]