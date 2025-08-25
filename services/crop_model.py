def predict_crop(soil_type: str, season: str, location: str, temperature: float, humidity: float) -> str:
    """
    Simple placeholder logic aligned with routes.CropRequest fields.
    Replace with real ML model later.
    """
    if soil_type.lower() == "clay" and season.lower() == "monsoon" and humidity > 70:
        return "Rice"
    if soil_type.lower() == "sandy" and season.lower() == "winter" and temperature < 20:
        return "Wheat"
    if soil_type.lower() == "loam" and season.lower() == "summer" and 20 <= temperature <= 30:
        return "Maize"
    return "Sugarcane"
