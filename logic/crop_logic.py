import pandas as pd

df = pd.read_csv("data/farmer_data.csv")
df.columns = df.columns.str.strip()


def calculate_diversity_score(recommended_crops):
    """
    Calculate crop diversity score based on recommended crops
    
    Args:
        recommended_crops: List of crop names
        
    Returns:
        dict with diversity analysis
    """
    unique_crops = len(set(recommended_crops))
    total_crops = len(recommended_crops)
    
    # Determine diversity level
    if unique_crops == 1:
        level = "LOW"
        message = "You are over-dependent on a single crop. Increasing crop diversity can improve soil health, reduce income risk, and enhance nutrition outcomes."
        recommendation = "Consider adding 2-3 different crops from other categories (pulses, oilseeds, vegetables) to diversify."
    elif unique_crops == 2:
        level = "MEDIUM"
        message = "Moderate crop diversity detected. Adding one more crop type would improve resilience."
        recommendation = "Consider adding a legume crop to fix nitrogen and improve soil health."
    else:
        level = "HIGH"
        message = "Good crop diversity improves nutrition outcomes, climate resilience, and soil health."
        recommendation = "Maintain this diversity pattern and consider crop rotation for optimal soil health."
    
    # Calculate crop category diversity (optional enhancement)
    crop_categories = categorize_crops([c.lower() for c in recommended_crops])
    unique_categories = len(set(crop_categories.values()))
    
    return {
        "level": level,
        "unique_crops": unique_crops,
        "total_recommendations": total_crops,
        "diversity_percentage": round((unique_crops / total_crops) * 100, 1),
        "unique_categories": unique_categories,
        "message": message,
        "recommendation": recommendation,
        "benefits": get_diversity_benefits(level)
    }


def categorize_crops(crop_names):
    """
    Categorize crops into groups for enhanced diversity analysis
    
    Returns:
        dict mapping crop_name -> category
    """
    categories = {
        # Cereals
        'rice': 'Cereal', 'paddy': 'Cereal', 'wheat': 'Cereal', 'maize': 'Cereal',
        'corn': 'Cereal', 'barley': 'Cereal', 'millet': 'Cereal', 'sorghum': 'Cereal',
        
        # Pulses/Legumes
        'chickpea': 'Pulse', 'lentil': 'Pulse', 'pigeon pea': 'Pulse', 
        'black gram': 'Pulse', 'green gram': 'Pulse', 'kidney beans': 'Pulse',
        'mung bean': 'Pulse', 'moth bean': 'Pulse',
        
        # Oilseeds
        'groundnut': 'Oilseed', 'peanut': 'Oilseed', 'soybean': 'Oilseed',
        'sunflower': 'Oilseed', 'mustard': 'Oilseed', 'sesame': 'Oilseed',
        'rapeseed': 'Oilseed',
        
        # Vegetables
        'tomato': 'Vegetable', 'potato': 'Vegetable', 'onion': 'Vegetable',
        'cabbage': 'Vegetable', 'cauliflower': 'Vegetable', 'brinjal': 'Vegetable',
        'okra': 'Vegetable', 'pumpkin': 'Vegetable',
        
        # Cash crops
        'cotton': 'Cash Crop', 'sugarcane': 'Cash Crop', 'jute': 'Cash Crop',
        'tobacco': 'Cash Crop', 'tea': 'Cash Crop', 'coffee': 'Cash Crop'
    }
    
    result = {}
    for crop in crop_names:
        result[crop] = categories.get(crop.lower(), 'Other')
    
    return result


def get_diversity_benefits(level):
    """Return specific benefits based on diversity level"""
    benefits = {
        "LOW": [
            "High risk of total crop failure",
            "Soil nutrient depletion from monoculture",
            "Limited nutrition diversity in diet"
        ],
        "MEDIUM": [
            "Reduced risk compared to single crop",
            "Some soil health benefits",
            "Moderate income stability"
        ],
        "HIGH": [
            "Reduced risk of total crop failure",
            "Improved soil health through varied root systems",
            "Better nutrition diversity for family",
            "Income stability from multiple sources",
            "Natural pest management through diversity"
        ]
    }
    return benefits.get(level, [])


def recommend_crop(input_data):
    limit = input_data.get("limit", 3)

    temp = input_data["temperature"]
    humidity = input_data["humidity"]
    moisture = input_data["moisture"]
    soil_type = input_data["soil_type"]

    n = input_data["nitrogen"]
    p = input_data["phosphorous"]
    k = input_data["potassium"]

    filtered = df[
        (abs(df["Temperature"] - temp) <= 3) &
        (abs(df["Humidity"] - humidity) <= 10) &
        (abs(df["Moisture"] - moisture) <= 10) &
        (df["Soil Type"].str.lower() == soil_type.lower())
    ]

    if filtered.empty:
        filtered = df[df["Soil Type"].str.lower() == soil_type.lower()]

    filtered = filtered.copy()
    filtered["npk_score"] = (
        abs(filtered["Nitrogen"] - n) +
        abs(filtered["Phosphorous"] - p) +
        abs(filtered["Potassium"] - k)
    )

    top_matches = filtered.sort_values("npk_score").head(15)

    crops = top_matches["Crop Type"].value_counts().head(limit)
    recommended_crops_list = crops.index.tolist()
    
    # Calculate diversity score
    diversity_analysis = calculate_diversity_score(recommended_crops_list)

    return {
        "recommended_crops": recommended_crops_list,
        "shown": limit,
        "note": "Showing best-matched crops based on soil, climate, and nutrients",
        "diversity_score": diversity_analysis
    }


def get_crop_details(input_data):
    """
    Get detailed explanation for why a specific crop was recommended
    """
    crop_name = input_data["crop_name"].lower()
    temp = input_data["temperature"]
    humidity = input_data["humidity"]
    moisture = input_data["moisture"]
    soil_type = input_data["soil_type"]
    n = input_data["nitrogen"]
    p = input_data["phosphorous"]
    k = input_data["potassium"]

    # Filter for this specific crop
    crop_data = df[df["Crop Type"].str.lower() == crop_name].copy()

    if crop_data.empty:
        return {
            "error": f"Crop '{crop_name}' not found in database",
            "crop_name": crop_name
        }

    # Calculate scores for all instances of this crop
    crop_data["temp_diff"] = abs(crop_data["Temperature"] - temp)
    crop_data["humidity_diff"] = abs(crop_data["Humidity"] - humidity)
    crop_data["moisture_diff"] = abs(crop_data["Moisture"] - moisture)
    crop_data["npk_score"] = (
        abs(crop_data["Nitrogen"] - n) +
        abs(crop_data["Phosphorous"] - p) +
        abs(crop_data["Potassium"] - k)
    )
    crop_data["soil_match"] = crop_data["Soil Type"].str.lower() == soil_type.lower()

    # Get the best match for this crop
    best_match = crop_data.sort_values("npk_score").iloc[0]

    # Calculate match percentages
    temp_match = max(0, 100 - (best_match["temp_diff"] / 3 * 100))
    humidity_match = max(0, 100 - (best_match["humidity_diff"] / 10 * 100))
    moisture_match = max(0, 100 - (best_match["moisture_diff"] / 10 * 100))
    
    # NPK match (inverse of score, normalized)
    max_npk_diff = 150  # Reasonable max difference
    npk_match = max(0, 100 - (best_match["npk_score"] / max_npk_diff * 100))

    # Overall suitability score
    overall_score = (
        temp_match * 0.25 +
        humidity_match * 0.25 +
        moisture_match * 0.20 +
        npk_match * 0.20 +
        (100 if best_match["soil_match"] else 50) * 0.10
    )

    # Generate explanation text
    explanations = []
    
    if temp_match > 80:
        explanations.append(f"✓ Temperature ({temp}°C) is ideal for {crop_name}")
    elif temp_match > 60:
        explanations.append(f"~ Temperature ({temp}°C) is acceptable for {crop_name}")
    else:
        explanations.append(f"⚠ Temperature ({temp}°C) is suboptimal (ideal: {best_match['Temperature']}°C)")

    if humidity_match > 80:
        explanations.append(f"✓ Humidity ({humidity}%) is perfect for {crop_name}")
    elif humidity_match > 60:
        explanations.append(f"~ Humidity ({humidity}%) is acceptable for {crop_name}")
    else:
        explanations.append(f"⚠ Humidity ({humidity}%) could be better (ideal: {best_match['Humidity']}%)")

    if moisture_match > 80:
        explanations.append(f"✓ Soil moisture ({moisture}%) is excellent for {crop_name}")
    elif moisture_match > 60:
        explanations.append(f"~ Soil moisture ({moisture}%) is adequate for {crop_name}")
    else:
        explanations.append(f"⚠ Soil moisture ({moisture}%) needs attention (ideal: {best_match['Moisture']}%)")

    if best_match["soil_match"]:
        explanations.append(f"✓ {soil_type.capitalize()} soil is perfect for {crop_name}")
    else:
        explanations.append(f"⚠ {soil_type.capitalize()} soil works, but {best_match['Soil Type']} is ideal")

    if npk_match > 70:
        explanations.append(f"✓ NPK levels (N:{n}, P:{p}, K:{k}) are well-balanced for {crop_name}")
    elif npk_match > 50:
        explanations.append(f"~ NPK levels are acceptable but could be optimized")
    else:
        explanations.append(f"⚠ Consider adjusting NPK to N:{best_match['Nitrogen']}, P:{best_match['Phosphorous']}, K:{best_match['Potassium']}")

    return {
        "crop_name": crop_name.capitalize(),
        "overall_score": round(overall_score, 1),
        "suitability": "Excellent" if overall_score > 80 else "Good" if overall_score > 60 else "Fair" if overall_score > 40 else "Poor",
        "climate_match": {
            "temperature": {
                "your_value": temp,
                "ideal_value": float(best_match["Temperature"]),
                "match_percentage": round(temp_match, 1),
                "status": "excellent" if temp_match > 80 else "good" if temp_match > 60 else "fair"
            },
            "humidity": {
                "your_value": humidity,
                "ideal_value": float(best_match["Humidity"]),
                "match_percentage": round(humidity_match, 1),
                "status": "excellent" if humidity_match > 80 else "good" if humidity_match > 60 else "fair"
            },
            "moisture": {
                "your_value": moisture,
                "ideal_value": float(best_match["Moisture"]),
                "match_percentage": round(moisture_match, 1),
                "status": "excellent" if moisture_match > 80 else "good" if moisture_match > 60 else "fair"
            }
        },
        "soil_match": {
            "your_soil": soil_type.capitalize(),
            "ideal_soil": best_match["Soil Type"],
            "is_perfect_match": bool(best_match["soil_match"]),
            "compatibility": "Perfect" if best_match["soil_match"] else "Compatible"
        },
        "nutrient_match": {
            "your_npk": {"N": n, "P": p, "K": k},
            "ideal_npk": {
                "N": int(best_match["Nitrogen"]),
                "P": int(best_match["Phosphorous"]),
                "K": int(best_match["Potassium"])
            },
            "match_percentage": round(npk_match, 1),
            "status": "excellent" if npk_match > 70 else "good" if npk_match > 50 else "fair"
        },
        "explanations": explanations,
        "recommendations": [
            "Plant during optimal season for best yield",
            "Monitor soil pH levels regularly",
            "Ensure proper irrigation based on moisture needs",
            "Consider crop rotation for soil health"
        ]
    }