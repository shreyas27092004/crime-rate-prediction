from pymongo import MongoClient
import pandas as pd

def fetch_data():
    
    client = MongoClient('mongodb://localhost:27017/')  
    db = client['nowhere']  
    collection = db['crimes']  

    
    data = list(collection.find())
    df = pd.DataFrame(data)
    
    return df

# df = fetch_data()
# print(df.head())
