import os
import pandas as pd
from pymongo import MongoClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Ensure model directory exists
os.makedirs("models", exist_ok=True)

client = MongoClient('mongodb://localhost:27017/')  
db = client['nowhere']  
collection = db['crimes']  


data = list(collection.find())
df = pd.DataFrame(data)

df = df[["DISTRICT", "DAY_OF_WEEK", "HOUR", "OFFENSE_CODE_GROUP"]].dropna()

# Encode categorical features
X = pd.get_dummies(df[["DISTRICT", "DAY_OF_WEEK", "HOUR"]])
y = df["OFFENSE_CODE_GROUP"]

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict and calculate accuracy
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Model trained with accuracy: {accuracy:.2f}")

# Save model to disk
joblib.dump(model, "models/crime_model.pkl")
