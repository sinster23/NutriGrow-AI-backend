# logic/nutrition_advisory.py

"""
Regional Nutrition Advisory System
Provides nutrition deficiency information based on geographic region
"""

# Regional nutrition data based on NFHS-5 and other sources
REGIONAL_NUTRITION_DATA = {
    # North India
    "uttar pradesh": {
        "deficiencies": ["Iron", "Protein", "Vitamin A"],
        "severity": "high",
        "message": "Iron and protein deficiencies are high in your region. Growing millets, pulses, and leafy vegetables can help improve community nutrition.",
        "recommended_crops": ["Pearl Millet", "Lentil", "Spinach", "Chickpea"],
        "stats": "45% of children under 5 are anemic in this region"
    },
    "bihar": {
        "deficiencies": ["Iron", "Zinc", "Vitamin A"],
        "severity": "very_high",
        "message": "Your region has critical iron and zinc deficiencies. Fortified crops and pulses are essential for community health.",
        "recommended_crops": ["Rice (Fortified)", "Lentil", "Pumpkin", "Chickpea"],
        "stats": "63% of children under 5 are anemic in this region"
    },
    "punjab": {
        "deficiencies": ["Vitamin D", "Calcium"],
        "severity": "moderate",
        "message": "Vitamin D and calcium deficiencies are common. Diversifying from wheat-rice to include vegetables and pulses can help.",
        "recommended_crops": ["Mustard Greens", "Chickpea", "Lentil", "Carrot"],
        "stats": "28% of children under 5 are anemic in this region"
    },
    "haryana": {
        "deficiencies": ["Iron", "Vitamin D"],
        "severity": "moderate",
        "message": "Iron deficiency is prevalent. Growing iron-rich crops alongside traditional wheat can improve nutrition.",
        "recommended_crops": ["Spinach", "Lentil", "Chickpea", "Bajra"],
        "stats": "32% of children under 5 are anemic in this region"
    },
    "delhi": {
        "deficiencies": ["Vitamin D", "Iron"],
        "severity": "moderate",
        "message": "Urban nutrition gaps include iron and vitamin D. Kitchen gardens with leafy vegetables can help.",
        "recommended_crops": ["Spinach", "Fenugreek", "Tomato", "Radish"],
        "stats": "35% of children under 5 are anemic in this region"
    },
    
    # East India
    "west bengal": {
        "deficiencies": ["Iron", "Vitamin A", "Zinc"],
        "severity": "high",
        "message": "Iron and vitamin A deficiencies are significant. Growing orange vegetables and pulses can address these gaps.",
        "recommended_crops": ["Pumpkin", "Carrot", "Lentil", "Rice (Fortified)"],
        "stats": "54% of children under 5 are anemic in this region"
    },
    "odisha": {
        "deficiencies": ["Iron", "Protein", "Vitamin A"],
        "severity": "very_high",
        "message": "Your region faces critical malnutrition. Millets, pulses, and vegetables are essential for community health.",
        "recommended_crops": ["Finger Millet", "Lentil", "Pumpkin", "Spinach"],
        "stats": "64% of children under 5 are anemic in this region"
    },
    "jharkhand": {
        "deficiencies": ["Iron", "Protein", "Zinc"],
        "severity": "very_high",
        "message": "Severe iron and protein deficiencies exist. Growing traditional millets and pulses can significantly improve nutrition.",
        "recommended_crops": ["Finger Millet", "Chickpea", "Lentil", "Amaranth"],
        "stats": "65% of children under 5 are anemic in this region"
    },
    
    # South India
    "karnataka": {
        "deficiencies": ["Iron", "Vitamin A"],
        "severity": "moderate",
        "message": "Iron deficiency is common. Including millets and leafy vegetables in farming can boost nutrition.",
        "recommended_crops": ["Finger Millet", "Spinach", "Tomato", "Lentil"],
        "stats": "42% of children under 5 are anemic in this region"
    },
    "tamil nadu": {
        "deficiencies": ["Iron", "Calcium"],
        "severity": "moderate",
        "message": "Iron and calcium deficiencies are present. Diversifying crops to include millets and greens can help.",
        "recommended_crops": ["Finger Millet", "Amaranth", "Spinach", "Lentil"],
        "stats": "38% of children under 5 are anemic in this region"
    },
    "kerala": {
        "deficiencies": ["Vitamin D", "Iron"],
        "severity": "low",
        "message": "Moderate iron deficiency exists. Kitchen gardens with vegetables can supplement nutrition.",
        "recommended_crops": ["Spinach", "Tomato", "Cucumber", "Beans"],
        "stats": "23% of children under 5 are anemic in this region"
    },
    "andhra pradesh": {
        "deficiencies": ["Iron", "Vitamin A"],
        "severity": "moderate",
        "message": "Iron deficiency is common. Growing millets alongside rice can improve community nutrition.",
        "recommended_crops": ["Pearl Millet", "Spinach", "Pumpkin", "Lentil"],
        "stats": "46% of children under 5 are anemic in this region"
    },
    
    # West India
    "maharashtra": {
        "deficiencies": ["Iron", "Vitamin A"],
        "severity": "moderate",
        "message": "Iron deficiency affects many areas. Growing millets and pulses can address nutritional gaps.",
        "recommended_crops": ["Pearl Millet", "Chickpea", "Spinach", "Tomato"],
        "stats": "39% of children under 5 are anemic in this region"
    },
    "gujarat": {
        "deficiencies": ["Iron", "Protein"],
        "severity": "moderate",
        "message": "Iron and protein gaps exist. Diversifying with pulses and vegetables can improve nutrition.",
        "recommended_crops": ["Chickpea", "Pearl Millet", "Spinach", "Peanut"],
        "stats": "41% of children under 5 are anemic in this region"
    },
    "rajasthan": {
        "deficiencies": ["Iron", "Vitamin A", "Zinc"],
        "severity": "high",
        "message": "High iron deficiency is present. Water-efficient millets and pulses are ideal for your region.",
        "recommended_crops": ["Pearl Millet", "Chickpea", "Lentil", "Cluster Beans"],
        "stats": "51% of children under 5 are anemic in this region"
    },
    
    # Northeast India
    "assam": {
        "deficiencies": ["Iron", "Vitamin A", "Iodine"],
        "severity": "high",
        "message": "Iron and vitamin A deficiencies are significant. Growing diverse vegetables can improve nutrition.",
        "recommended_crops": ["Rice (Fortified)", "Pumpkin", "Spinach", "Lentil"],
        "stats": "52% of children under 5 are anemic in this region"
    },
    "meghalaya": {
        "deficiencies": ["Iron", "Protein"],
        "severity": "high",
        "message": "High malnutrition rates exist. Growing protein-rich crops and vegetables is essential.",
        "recommended_crops": ["Rice", "Lentil", "Beans", "Pumpkin"],
        "stats": "48% of children under 5 are anemic in this region"
    },
    
    # Central India
    "madhya pradesh": {
        "deficiencies": ["Iron", "Protein", "Vitamin A"],
        "severity": "high",
        "message": "Iron and protein deficiencies are widespread. Millets and pulses are crucial for better nutrition.",
        "recommended_crops": ["Pearl Millet", "Chickpea", "Lentil", "Spinach"],
        "stats": "50% of children under 5 are anemic in this region"
    },
    "chhattisgarh": {
        "deficiencies": ["Iron", "Protein", "Zinc"],
        "severity": "very_high",
        "message": "Critical malnutrition exists. Growing millets and pulses can significantly improve community health.",
        "recommended_crops": ["Finger Millet", "Lentil", "Chickpea", "Amaranth"],
        "stats": "62% of children under 5 are anemic in this region"
    },
}

# Default for unknown regions
DEFAULT_ADVISORY = {
    "deficiencies": ["Iron", "Protein"],
    "severity": "moderate",
    "message": "Iron and protein deficiencies are common across India. Growing diverse crops including millets, pulses, and vegetables can improve nutrition.",
    "recommended_crops": ["Pearl Millet", "Lentil", "Spinach", "Chickpea"],
    "stats": "National average: 40% of children under 5 are anemic"
}


def get_regional_nutrition_advisory(region: str) -> dict:
    """
    Get nutrition advisory for a specific region
    
    Args:
        region: Name of the state/region (case-insensitive)
        
    Returns:
        dict: Regional nutrition data with deficiencies and recommendations
    """
    region_normalized = region.lower().strip()
    
    advisory = REGIONAL_NUTRITION_DATA.get(region_normalized, DEFAULT_ADVISORY.copy())
    
    return {
        "region": region.title(),
        "deficiencies": advisory["deficiencies"],
        "severity": advisory["severity"],
        "message": advisory["message"],
        "recommended_crops": advisory["recommended_crops"],
        "statistics": advisory["stats"],
        "awareness_note": "This information is based on national health surveys and can help guide crop selection for better community nutrition."
    }


def get_severity_color(severity: str) -> str:
    """Get color code based on severity level"""
    colors = {
        "very_high": "#dc2626",  # red-600
        "high": "#ea580c",       # orange-600
        "moderate": "#f59e0b",   # amber-500
        "low": "#10b981"         # emerald-500
    }
    return colors.get(severity, "#6b7280")  # gray-500 as default