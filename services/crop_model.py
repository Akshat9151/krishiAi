from fastapi import APIRouter

router = APIRouter()

@router.get("/recommend")
def recommend_crop(soil: str, season: str):
    # simple dummy logic
    if soil == "clay" and season == "summer":
        return {"crop": "Rice"}
    elif soil == "sandy" and season == "winter":
        return {"crop": "Wheat"}
    return {"crop": "Maize"}
# services/crop_model.py

def predict_crop(nitrogen: float, phosphorus: float, potassium: float, ph: float, rainfall: float):
    """
    Simple crop prediction logic (dummy example).
    Aap isko apne ML model se replace kar sakte ho.
    """
    if nitrogen > 50 and rainfall > 200:
        return "Rice"
    elif phosphorus > 40:
        return "Wheat"
    elif potassium > 30 and ph >= 6:
        return "Sugarcane"
    else:
        return "Maize"
