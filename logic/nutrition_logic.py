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
            (filtered["Cholesterol"] <= 100)
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

