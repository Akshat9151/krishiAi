# routes.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services.crop_model import predict_crop
from services.auth import get_current_user

router = APIRouter()

class CropRequest(BaseModel):
    soil_type: str
    season: str
    location: str
    temperature: float
    humidity: float

@router.post("/predict-crop")
def predict_crop_route(data: CropRequest):
    try:
        crop = predict_crop(
            soil_type=data.soil_type,
            season=data.season,
            location=data.location,
            temperature=data.temperature,
            humidity=data.humidity
        )
        return {"recommended_crop": crop}
    except Exception as e:
        return {"error": str(e)}

@router.get("/health")
def health_check():
    return {"status": "ok", "service": "Krishi AI"}


@router.get("/recommend_crop_auto/{soil_type}/{city}/{season}")
def recommend_crop_auto(
    soil_type: str, 
    city: str, 
    season: str, 
    current_user: str = Depends(get_current_user)
):
    """Auto crop recommendation with mock weather data"""
    try:
        # Mock weather data for demo purposes
        # In production, you would fetch real weather data from an API
        mock_weather = {
            "mumbai": {"temperature": 28.5, "humidity": 75},
            "delhi": {"temperature": 25.2, "humidity": 60},
            "bangalore": {"temperature": 22.8, "humidity": 70},
            "chennai": {"temperature": 30.1, "humidity": 80},
            "kolkata": {"temperature": 27.3, "humidity": 78}
        }
        
        city_lower = city.lower()
        weather_data = mock_weather.get(city_lower, {"temperature": 25.0, "humidity": 65})
        
        # Mock crop recommendation logic
        crop_recommendations = {
            ("clay", "summer"): ["rice", "cotton", "sugarcane"],
            ("clay", "winter"): ["wheat", "barley", "mustard"],
            ("clay", "monsoon"): ["rice", "jute", "pulses"],
            ("sandy", "summer"): ["millet", "groundnut", "cotton"],
            ("sandy", "winter"): ["gram", "lentil", "mustard"],
            ("sandy", "monsoon"): ["bajra", "jowar", "pulses"],
            ("loamy", "summer"): ["maize", "cotton", "sugarcane"],
            ("loamy", "winter"): ["wheat", "potato", "peas"],
            ("loamy", "monsoon"): ["rice", "soybean", "cotton"]
        }
        
        key = (soil_type.lower(), season.lower())
        recommended_crops = crop_recommendations.get(key, ["wheat", "rice", "maize"])
        
        return {
            "location": city.title(),
            "soil_type": soil_type.title(),
            "season": season.title(),
            "temperature": weather_data["temperature"],
            "humidity": weather_data["humidity"],
            "recommended_crops": recommended_crops,
            "user": current_user
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting crop recommendation: {str(e)}")


@router.post("/contact")
def contact_form(
    contact_data: dict,
    current_user: str = Depends(get_current_user)
):
    """Handle contact form submissions"""
    try:
        # In a real application, you would save this to database or send email
        return {"message": f"Thank you {contact_data.get('name', 'User')}! Your message has been received. ✅"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing contact form: {str(e)}")
