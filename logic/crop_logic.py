import pandas as pd

df = pd.read_csv("data/farmer_data.csv")
df.columns = df.columns.str.strip()


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

    return {
        "recommended_crops": crops.index.tolist(),
        "shown": limit,
        "note": "Showing best-matched crops based on soil, climate, and nutrients"
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