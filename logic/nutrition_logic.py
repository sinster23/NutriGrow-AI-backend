import pandas as pd

df = pd.read_csv(
    "data/consumer_data.csv",
    engine="python",
    on_bad_lines="skip"
)
df.columns = df.columns.str.strip()


def nutrition_plan(input_data):
    age = input_data["age"]
    bmi = input_data["bmi"]
    condition = input_data["condition"].lower()
    diet = input_data["diet"].lower()

    filtered = df.copy()

    # 1️⃣ Diet preference
    if diet == "vegetarian":
        filtered = filtered[~filtered["Category"].str.contains(
            "meat|fish|chicken", case=False, na=False)]

    # 2️⃣ Age-based filtering (safety)
    if age < 18:
        filtered = filtered[
            (filtered["Sodium (mg)"] <= 200) &
            (filtered["Cholesterol (mg)"] <= 100)
        ]
    elif age > 40:
        filtered = filtered[
            (filtered["Sodium (mg)"] <= 150) &
            (filtered["Sugars (g)"] <= 10)
        ]

    # 3️⃣ BMI-based logic (main nutrition driver)
    if bmi < 18.5:
        filtered = filtered[filtered["Calories (kcal)"] >= 150]
    elif bmi >= 25:
        filtered = filtered[filtered["Calories (kcal)"] <= 300]

    # 4️⃣ Health condition fine-tuning
    if condition == "diabetes":
        filtered = filtered[filtered["Sugars (g)"] <= 5]
    elif condition == "anemia":
        filtered = filtered[filtered["Protein (g)"] >= 5]

    # 5️⃣ Ranking logic
    filtered = filtered.sort_values(
        by=["Protein (g)", "Calories (kcal)"],
        ascending=False
        )

    limit = input_data.get("limit", 4)

    top_foods = (
        filtered
        .drop_duplicates(subset=["Food_Item"])
        .head(limit)
    )

    return {
        "recommended_foods": top_foods["Food_Item"].tolist(),
        "shown": limit,
        "note": "Recommendations personalized using age, BMI, and health condition"
    }

def get_food_details(input_data):
    food_name = input_data["food_name"].strip().lower()
    age = input_data["age"]
    bmi = input_data["bmi"]
    condition = input_data["condition"].lower()
    diet = input_data["diet"].lower()

    # Filter dataset for the selected food
    food_data = df[df["Food_Item"].str.lower() == food_name].copy()

    if food_data.empty:
        return {
            "error": f"Food item '{food_name}' not found in dataset",
            "food_name": food_name
        }

    # Use first matching row
    food = food_data.iloc[0]

    explanations = []
    specific_benefits = []

    # Calculate match scores (more nuanced scoring)
    diet_match = 0
    condition_match = 0
    bmi_match = 0
    age_match = 0

    # 1️⃣ Diet suitability
    if diet == "vegetarian":
        is_veg = not any(x in str(food.get("Category", "")).lower() for x in ["meat", "fish", "chicken", "egg"])
        if is_veg:
            diet_match = 100
            explanations.append("✓ Suitable for a vegetarian diet")
            specific_benefits.append("Plant-based nutrition that aligns with vegetarian principles")
        else:
            diet_match = 0
            explanations.append("⚠ Contains non-vegetarian ingredients")
    else:
        # For non-veg, check if it's a balanced choice
        diet_match = 85  # Good baseline, not perfect by default
        explanations.append("✓ Suitable for a non-vegetarian diet")

    # 2️⃣ Age-based reasoning (more granular scoring)
    sodium = food["Sodium (mg)"]
    cholesterol = food["Cholesterol (mg)"]
    
    if age < 18:
        # Youth - stricter requirements
        if sodium <= 150 and cholesterol <= 80:
            age_match = 100
            explanations.append("✓ Excellent sodium and cholesterol levels for youth")
            specific_benefits.append("Optimal nutrient levels for growing bodies")
        elif sodium <= 200 and cholesterol <= 100:
            age_match = 75
            explanations.append("✓ Acceptable sodium and cholesterol for younger individuals")
        else:
            age_match = 40
            explanations.append("⚠ Higher sodium/cholesterol - consume occasionally")
    elif age > 40:
        # Seniors - focus on heart health
        if sodium <= 100 and food["Sugars (g)"] <= 8:
            age_match = 100
            explanations.append("✓ Excellent heart-friendly nutrition")
            specific_benefits.append("Very low sodium supports cardiovascular health")
        elif sodium <= 150 and food["Sugars (g)"] <= 10:
            age_match = 80
            explanations.append("✓ Good sodium and sugar levels for mature adults")
        else:
            age_match = 50
            explanations.append("⚠ Moderate sodium/sugar - watch portion sizes")
    else:
        # Adults 18-40
        if sodium <= 200 and cholesterol <= 150:
            age_match = 90
            explanations.append("✓ Well-balanced for active adults")
        else:
            age_match = 65
            explanations.append("✓ Suitable with mindful consumption")

    # 3️⃣ BMI-based reasoning (gradual scoring)
    calories = food["Calories (kcal)"]
    
    if bmi < 18.5:
        # Underweight - need calorie-dense foods
        if calories >= 250:
            bmi_match = 100
            explanations.append("✓ Calorie-dense food ideal for healthy weight gain")
            specific_benefits.append("High energy content supports weight increase")
        elif calories >= 150:
            bmi_match = 70
            explanations.append("✓ Moderate calories support gradual weight gain")
        else:
            bmi_match = 40
            explanations.append("⚠ Low calorie - pair with energy-rich foods")
    elif bmi >= 25:
        # Overweight - need lower calorie options
        if calories <= 150:
            bmi_match = 100
            explanations.append("✓ Low calorie content excellent for weight management")
            specific_benefits.append("Calorie-controlled nutrition for healthy weight loss")
        elif calories <= 250:
            bmi_match = 75
            explanations.append("✓ Moderate calories manageable with portion control")
        else:
            bmi_match = 45
            explanations.append("⚠ Higher calories - use small portions")
    else:
        # Normal BMI - balanced approach
        if 150 <= calories <= 300:
            bmi_match = 95
            explanations.append("✓ Perfectly balanced calorie content")
        elif calories < 150 or calories > 300:
            bmi_match = 70
            explanations.append("✓ Calorie level workable with balanced meal planning")
        else:
            bmi_match = 80
            explanations.append("✓ Calorie content aligns with your BMI")

    # 4️⃣ Health condition reasoning (more detailed)
    sugar = food["Sugars (g)"]
    protein = food["Protein (g)"]
    
    if condition == "diabetes":
        if sugar <= 3:
            condition_match = 100
            explanations.append("✓ Very low sugar - excellent for diabetes management")
            specific_benefits.append("Minimal blood sugar impact, ideal for diabetics")
        elif sugar <= 5:
            condition_match = 80
            explanations.append("✓ Low sugar content supports blood sugar control")
            specific_benefits.append("Acceptable sugar levels for diabetes management")
        elif sugar <= 10:
            condition_match = 50
            explanations.append("⚠ Moderate sugar - consume in small portions")
        else:
            condition_match = 20
            explanations.append("⚠ High sugar content - not recommended")
    elif condition == "anemia":
        if protein >= 8:
            condition_match = 100
            explanations.append("✓ High protein excellent for anemia management")
            specific_benefits.append("Rich protein supports iron absorption and blood health")
        elif protein >= 5:
            condition_match = 75
            explanations.append("✓ Good protein content supports iron-rich diet")
            specific_benefits.append("Adequate protein for blood health support")
        else:
            condition_match = 45
            explanations.append("⚠ Lower protein - pair with protein-rich foods")
    elif condition == "hypertension":
        if sodium <= 100:
            condition_match = 100
            explanations.append("✓ Very low sodium - perfect for blood pressure control")
            specific_benefits.append("Minimal sodium impact on blood pressure")
        elif sodium <= 150:
            condition_match = 75
            explanations.append("✓ Low sodium supports hypertension management")
        else:
            condition_match = 40
            explanations.append("⚠ Higher sodium - monitor blood pressure")
    else:
        # No specific condition - evaluate overall nutritional balance
        balance_score = 0
        if protein >= 5:
            balance_score += 30
        if sugar <= 10:
            balance_score += 30
        if sodium <= 200:
            balance_score += 25
        if calories >= 100:
            balance_score += 15
        
        condition_match = balance_score
        if condition_match >= 80:
            explanations.append("✓ Excellent nutritional balance for general wellness")
        else:
            explanations.append("✓ Suitable for general health maintenance")

    # Calculate overall match
    overall_match = round((diet_match + condition_match + bmi_match + age_match) / 4)

    # Determine BMI category
    if bmi < 18.5:
        bmi_category = "Underweight"
    elif 18.5 <= bmi < 25:
        bmi_category = "Normal"
    elif 25 <= bmi < 30:
        bmi_category = "Overweight"
    else:
        bmi_category = "Obese"

    # Determine age group
    if age < 18:
        age_group = "Youth"
    elif age < 40:
        age_group = "Adult"
    else:
        age_group = "Senior"

    # Generate recommendation reason
    recommendation_reason = f"This food was selected based on your profile: {age_group.lower()} aged {age}, {bmi_category.lower()} BMI of {bmi}, following a {diet} diet"
    if condition != "none":
        recommendation_reason += f", with {condition} as a health consideration"
    recommendation_reason += ". The nutritional composition aligns well with your specific needs."

    # Generate suitability summary
    suitability_score = overall_match
    if suitability_score >= 80:
        suitability = "Excellent choice! This food is highly recommended for your health profile and meets your dietary requirements exceptionally well."
    elif suitability_score >= 60:
        suitability = "Good option. This food generally aligns with your health needs, though some considerations may apply."
    else:
        suitability = "Moderate fit. While this food can be part of your diet, consider portion sizes and pairing with complementary foods."

    return {
        "food_name": food["Food_Item"],
        "serving_size": "100g",  # Standard serving
        "overall_match": overall_match,
        "match_breakdown": {
            "diet_compatibility": diet_match,
            "condition_suitability": condition_match,
            "bmi_alignment": bmi_match,
            "age_appropriateness": age_match
        },
        "calories": float(food["Calories (kcal)"]),
        "protein": float(food["Protein (g)"]),
        "carbs": float(food.get("Carbohydrates (g)", 0)),
        "sugars": float(food["Sugars (g)"]),
        "sodium": float(food["Sodium (mg)"]),
        "cholesterol": float(food["Cholesterol (mg)"]),
        "recommendation_reason": recommendation_reason,
        "suitability": suitability,
        "dietary_info": {
            "diet_type": diet.capitalize(),
            "age_group": age_group,
            "bmi_category": bmi_category,
            "suitable_for": condition.capitalize() if condition != "none" else "General wellness"
        },
        "specific_benefits": specific_benefits,
        "explanations": explanations,
        "note": "Detailed analysis based on age, BMI, health condition, and dietary preference"
    }
