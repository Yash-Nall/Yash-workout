import os

import requests
import streamlit as st


def _credentials():
    key = (os.getenv("FATSECRET_KEY") or "").strip()
    secret = (os.getenv("FATSECRET_SECRET") or "").strip()
    if key and secret:
        return key, secret
    try:
        s = st.secrets
        if "FATSECRET_KEY" in s and "FATSECRET_SECRET" in s:
            return str(s["FATSECRET_KEY"]).strip(), str(s["FATSECRET_SECRET"]).strip()
    except Exception:
        pass
    return "", ""


def _off_pick_numeric(nutriments, *keys):
    for k in keys:
        v = nutriments.get(k)
        if v is None:
            continue
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            try:
                return float(v.strip())
            except ValueError:
                continue
    return None


def _off_rank(name: str, query: str) -> tuple:
    """Sort key: closer match to search query first."""
    nl = name.lower()
    ql = query.lower().strip()
    if not ql:
        return (3, name.lower())
    if nl.startswith(ql):
        return (0, len(name))
    if f" {ql}" in f" {nl}":
        return (1, nl.find(ql))
    if ql in nl:
        return (2, nl.find(ql))
    return (3, name.lower())


def _open_food_facts_product_to_row(product):
    code = str(product.get("code") or "").strip()
    name = (
        product.get("product_name_en")
        or product.get("product_name")
        or product.get("generic_name_en")
        or product.get("generic_name")
        or ""
    )
    name = str(name).strip()
    if not name and code:
        name = f"Product {code}"
    if not name:
        return None

    brand = (product.get("brands") or "").strip()
    img = (
        (product.get("image_front_small_url") or product.get("image_front_url") or "")
        or ""
    ).strip()

    food_url = f"https://world.openfoodfacts.org/product/{code}/" if code else "#"
    n = product.get("nutriments") or {}

    kcal = _off_pick_numeric(
        n,
        "energy-kcal_serving",
        "energy_kcal_serving",
        "energy-kcal_100g",
        "energy-kcal",
    )
    fat = _off_pick_numeric(n, "fat_serving", "fat_100g", "fat")
    carbs = _off_pick_numeric(
        n, "carbohydrates_serving", "carbohydrates_100g", "carbohydrates"
    )
    protein = _off_pick_numeric(
        n,
        "proteins_serving",
        "proteins_100g",
        "protein_serving",
        "protein_100g",
        "proteins",
    )

    qty = (product.get("quantity") or "").strip()
    if _off_pick_numeric(n, "energy-kcal_serving", "energy_kcal_serving") is not None:
        basis = "per serving"
    else:
        basis = "per 100g"
    if qty:
        basis = qty

    def fmt_macro(val):
        if val is None:
            return "—"
        return f"{val:g}g"

    cal_part = f"{kcal:g}kcal" if kcal is not None else "—"
    desc = (
        f"{basis} - Calories: {cal_part} | Fat: {fmt_macro(fat)} | "
        f"Carbs: {fmt_macro(carbs)} | Protein: {fmt_macro(protein)}"
    )

    return {
        "food_name": name,
        "food_url": food_url,
        "food_description": desc,
        "brand": brand,
        "image_url": img,
        "serving_label": basis,
        "calories": kcal,
        "fat_g": fat,
        "carbs_g": carbs,
        "protein_g": protein,
    }


_OFF_HEADERS = {
    "User-Agent": "WorkoutRecommender/1.0 (local nutrition search; not for bulk scraping)",
    "Accept": "application/json",
}


def _search_open_food_facts(query, page_size=24):
    url = "https://world.openfoodfacts.org/api/v2/search"
    params = {
        "search_terms": query,
        "page_size": page_size,
        "fields": (
            "code,product_name,product_name_en,generic_name,quantity,nutriments,"
            "brands,image_front_small_url,image_front_url"
        ),
    }
    try:
        r = requests.get(url, params=params, headers=_OFF_HEADERS, timeout=25)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []

    rows = []
    for p in data.get("products") or []:
        row = _open_food_facts_product_to_row(p)
        if row:
            rows.append(row)

    q = query.strip()
    rows.sort(key=lambda r: (_off_rank(r["food_name"], q), r["food_name"].lower()))
    return rows


def _search_fatsecret(query):
    key, secret = _credentials()
    if not key or not secret:
        return None
    try:
        from fatsecret_platform import FatSecret
        from fatsecret.errors import AuthenticationError

        client = Fatsecret(key, secret)
        return client.foods_search(query)
    except AuthenticationError:
        return None
    except Exception:
        return None


def _fatsecret_item_to_row(item):
    if not isinstance(item, dict):
        return None
    name = item.get("food_name") or item.get("food_description") or "Unknown"
    desc = item.get("food_description") or ""
    url = item.get("food_url") or "#"
    return {
        "food_name": str(name),
        "food_url": str(url),
        "food_description": str(desc),
        "brand": "",
        "image_url": "",
        "serving_label": "",
        "calories": None,
        "fat_g": None,
        "carbs_g": None,
        "protein_g": None,
    }


def search_foods(query):
    q = (query or "").strip()
    if not q:
        return []

    off = _search_open_food_facts(q)
    if off:
        return off

    fs = _search_fatsecret(q) or []
    out = []
    for item in fs:
        row = _fatsecret_item_to_row(item)
        if row:
            out.append(row)
    return out
