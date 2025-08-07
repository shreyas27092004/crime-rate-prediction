from pymongo import MongoClient
import pandas as pd
import os

def load_crime_data():
    try:

        # client = MongoClient('mongodb://localhost:27017/')        
        # db = client["nowhere"]
        # collection = db["crimes"]

        
        # data = list(collection.find())
        # if not data:
        #     return None 

        # df = pd.DataFrame(data)
        # df = df.drop(columns=['_id'], errors='ignore') 
        
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(base_path, "data", "crime.csv")
        print("Loading CSV from:", csv_path)  # Debug

        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(csv_path, encoding='latin1')  # fallback

        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None  
