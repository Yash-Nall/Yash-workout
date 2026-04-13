import requests
import streamlit as st


# =========================================================
# USDA API (BASE FOODS: chicken, rice, eggs, etc.)
# =========================================================

def _usda_search(query):
    api_key = st.secrets.get("USDA_API_KEY", "")
    if not api_key:
        return []

    url = "https://api.nal.usda.gov/fdc/v1/foods/search"

    params = {
        "query": query,
        "pageSize": 8,
        "api_key": api_key
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []

    results = []

    for item in data.get("foods", []):

        nutrients = item.get("foodNutrients", [])

        def get(nutrient_id):
            for n in nutrients:
                if n.get("nutrientId") == nutrient_id:
                    return n.get("value")
            return None

        calories = get(1008)
        protein = get(1003)
        carbs = get(1005)
        fat = get(1004)

        name = item.get("description", "Unknown food")
        fdc_id = item.get("fdcId")

        results.append({
            "food_name": name,
            "food_description": f"Calories: {calories or '—'} kcal | Protein: {protein or '—'}g | Carbs: {carbs or '—'}g | Fat: {fat or '—'}g",
            "food_url": f"https://fdc.nal.usda.gov/food-details/{fdc_id}/nutrients",
            "brand": "USDA",
            "image_url": "",
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat,
            "source": "USDA"
        })

    return results


# =========================================================
# OPEN FOOD FACTS (BRANDED FOODS: whey protein, snacks)
# =========================================================

def _off_search(query):
    url = "https://world.openfoodfacts.org/api/v2/search"

    params = {
        "search_terms": query,
        "page_size": 8,
        "fields": "code,product_name,brands,nutriments,image_front_small_url"
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []

    results = []

    for p in data.get("products", []):

        name = p.get("product_name") or "Unknown product"
        brand = p.get("brands") or "Unknown brand"
        code = p.get("code")

        n = p.get("nutriments", {})

        calories = n.get("energy-kcal_100g")
        protein = n.get("proteins_100g")
        carbs = n.get("carbohydrates_100g")
        fat = n.get("fat_100g")

        results.append({
            "food_name": name,
            "food_description": f"Calories: {calories or '—'} kcal | Protein: {protein or '—'}g | Carbs: {carbs or '—'}g | Fat: {fat or '—'}g",
            "food_url": f"https://world.openfoodfacts.org/product/{code}" if code else "#",
            "brand": brand,
            "image_url": p.get("image_front_small_url", ""),
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat,
            "source": "OFF"
        })

    return results


# =========================================================
# HYBRID MERGE ENGINE (THE MAGIC 🔥)
# =========================================================

def search_foods(query):
    q = (query or "").strip()
    if not q:
        return []

    usda = _usda_search(q)
    off = _off_search(q)

    # Merge results (USDA first = cleaner nutrition)
    combined = usda + off

    # Remove duplicates by name (simple dedupe)
    seen = set()
    final = []

    for item in combined:
        name = item["food_name"].lower()
        if name in seen:
            continue
        seen.add(name)
        final.append(item)

    return final
