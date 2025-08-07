import joblib

model = joblib.load("models/crime_model.pkl")

print(type(model))  

print(model.feature_importances_)

print(len(model.estimators_))  

print(model.estimators_[0])
