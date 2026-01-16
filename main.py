import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from logic.crop_logic import recommend_crop, get_crop_details
from logic.nutrition_logic import nutrition_plan, get_food_details
from logic.nutrition_advisory import get_regional_nutrition_advisory
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="NutriGrow AI Backend",
    description="Smart Crop-to-Nutrition Recommendation System",
    version="1.0"
)

# Get environment variables with fallback defaults
DEBUG = os.getenv("DEBUG", "False") == "True"
PORT = int(os.getenv("PORT", "8001"))
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

# CORS origins from environment
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:3000,http://127.0.0.1:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Example: Using API key from environment
API_KEY = os.getenv("API_KEY")
if not API_KEY and ENVIRONMENT == "production":
    raise ValueError("API_KEY must be set in production")

class FarmerInput(BaseModel):
    temperature: float
    humidity: float
    moisture: float
    soil_type: str
    nitrogen: float
    phosphorous: float
    potassium: float
    limit: int = 3  


class ConsumerInput(BaseModel):
    age: int
    bmi: float
    condition: str
    diet: str
    limit: int = 4


class CropDetailsInput(BaseModel):
    crop_name: str
    temperature: float
    humidity: float
    moisture: float
    soil_type: str
    nitrogen: float
    phosphorous: float
    potassium: float


class FoodDetailsInput(BaseModel):
    food_name: str
    age: int
    bmi: float
    condition: str
    diet: str

class RegionInput(BaseModel):
    region: str


@app.get("/")
def root():
    return {"message": "NutriGrow AI backend is running"}


@app.post("/recommend-crop")
def crop_recommendation(data: FarmerInput):
    return recommend_crop(data.dict())


@app.post("/crop-details")
def crop_details(data: CropDetailsInput):
    return get_crop_details(data.dict())


@app.post("/nutrition-plan")
def nutrition_recommendation(data: ConsumerInput):
    return nutrition_plan(data.dict())


@app.post("/food-details")
def food_details(data: FoodDetailsInput):
    return get_food_details(data.dict())

@app.post("/region-nutrition-advisory")
def region_nutrition_advisory(data: RegionInput):
    """Get nutrition advisory for a specific region"""
    return get_regional_nutrition_advisory(data.region)