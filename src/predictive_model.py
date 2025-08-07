import joblib
import pandas as pd

def load_model():
    return joblib.load("models/crime_model.pkl")

def make_prediction(model, input_data):
    df = pd.DataFrame([input_data])
    df = pd.get_dummies(df)

    model_features = model.feature_names_in_
    for col in model_features:
        if col not in df.columns:
            df[col] = 0
    df = df[model_features]

    prediction = model.predict(df)[0]
    return prediction
