# routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.crop_model import predict_crop

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
