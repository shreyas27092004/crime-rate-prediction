from pymongo import MongoClient
import pandas as pd

client = MongoClient("mongodb://localhost:27017/")
db = client["nowhere"]  
collection = db["crimes"] 


df = pd.read_csv("../data/crime.csv", encoding='latin1') 

df = df.dropna(subset=["HOUR", "MONTH", "DAY_OF_WEEK", "OFFENSE_CODE"])

collection.insert_many(df.to_dict(orient="records"))

print("✅ Data successfully added to MongoDB.")
