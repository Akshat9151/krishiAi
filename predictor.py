# predictor.py
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib
import os

# ------------------- Model Training (One-time) -------------------
# Dummy dataset (replace with real agricultural dataset)
data = {
    "temperature": [20, 25, 30, 35, 40, 22, 28, 32],
    "humidity": [30, 40, 50, 60, 70, 65, 55, 45],
    "soil_type": ["sandy", "loamy", "clay", "loamy", "sandy", "clay", "loamy", "sandy"],
    "season": ["rabi", "kharif", "rabi", "kharif", "rabi", "kharif", "rabi", "kharif"],
    "crop": ["wheat", "rice", "wheat", "rice", "wheat", "rice", "wheat", "rice"],
}

df = pd.DataFrame(data)

# Encode categorical data
df["soil_type"] = df["soil_type"].astype("category").cat.codes
df["season"] = df["season"].astype("category").cat.codes
df["crop"] = df["crop"].astype("category")

# Mapping dictionary for decoding predictions
crop_mapping = dict(enumerate(df["crop"].cat.categories))

X = df.drop("crop", axis=1)
y = df["crop"].cat.codes

# Train model only if not saved
MODEL_FILE = "model.pkl"

if not os.path.exists(MODEL_FILE):
    model = DecisionTreeClassifier()
    model.fit(X, y)
    joblib.dump(model, MODEL_FILE)
else:
    model = joblib.load(MODEL_FILE)

# ------------------- Predictor Function -------------------
def predict_crop(input_data: dict) -> str:
    """
    input_data = {
        "temperature": float,
        "humidity": float,
        "soil_type": "sandy/loamy/clay",
        "season": "rabi/kharif"
    }
    """
    soil_types = {"sandy": 0, "loamy": 1, "clay": 2}
    seasons = {"rabi": 1, "kharif": 0}

    try:
        features = np.array([[
            input_data["temperature"],
            input_data["humidity"],
            soil_types.get(input_data["soil_type"].lower(), 0),
            seasons.get(input_data["season"].lower(), 0)
        ]])

        prediction = model.predict(features)[0]
        return crop_mapping[prediction]

    except Exception as e:
        return f"Error in prediction: {str(e)}"
