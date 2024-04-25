from pymongo import MongoClient
import pandas as pd

# Connect to MongoDB
client = MongoClient("mongodb+srv://ramshabscsf19:sMzCIIY97F52CflR@cluster0.1txdpcy.mongodb.net/", 1687)

# Get the database and collection
db = client["rimsha"]
collection = db["data"]

dataset = pd.read_csv("religion_only.csv")

for i in range(len(dataset)):
    # convert each row to dict
    print(dataset.iloc[i, :]['text'])
    # data_dict = dict(dataset.iloc[i,:])
    # # insert dict to mongodb
    collection.insert_one({
        "id": i,
        "text": dataset.iloc[i, :]['text'],
    })

# Close the database connection
client.close()
