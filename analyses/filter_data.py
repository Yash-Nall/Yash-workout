import re

import pandas as pd


def _tokens(value):
    """Turn include/exclude input into a list of non-empty filter tokens."""
    if value is None or value == "None" or value == "":
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    return [str(x).strip() for x in value if x is not None and str(x).strip() and str(x) != "None"]


def _series_matches_any(series, tokens):
    """True where the string column contains any token as a substring (case-insensitive)."""
    tokens = _tokens(tokens)
    if not tokens:
        return pd.Series(True, index=series.index)
    pattern = "|".join(re.escape(t) for t in tokens)
    return series.fillna("").astype(str).str.contains(pattern, case=False, regex=True, na=False)


def _cell_matches_muscle_selection(target_cell: str, selected: str) -> bool:
    """
    True if a comma-separated muscle cell matches one user-selected muscle label.

    Uses segment and whole-word rules so "Chest" matches "Chest", "Upper Chest", and
    "Lower Chest", but does not match unrelated lines like "Shoulders, Triceps".
    """
    sel = selected.strip()
    if not sel:
        return False
    sel_lower = sel.lower()
    parts = [p.strip() for p in str(target_cell).split(",") if p and str(p).strip()]
    for part in parts:
        pl = part.lower()
        if pl == sel_lower:
            return True
        if " " in sel:
            pat = r"(?<![A-Za-z])" + re.escape(sel) + r"(?![A-Za-z])"
            if re.search(pat, part, re.IGNORECASE):
                return True
        else:
            words = re.findall(r"[A-Za-z]+", part)
            if sel_lower in {w.lower() for w in words}:
                return True
    return False


def _series_matches_muscles(series, tokens):
    """OR across selected muscles; each must match the cell via _cell_matches_muscle_selection."""
    tokens = _tokens(tokens)
    if not tokens:
        return pd.Series(True, index=series.index)

    def row_match(val: str) -> bool:
        return any(_cell_matches_muscle_selection(val, t) for t in tokens)

    return series.fillna("").astype(str).map(row_match)


def _difficulty_levels(difficulty):
    """Normalize difficulty input to a list of level names, or [] if no filter."""
    if difficulty in (None, "All", "", []):
        return []
    if isinstance(difficulty, str):
        return [difficulty] if difficulty != "All" else []
    return [d for d in difficulty if d and d != "All"]


def filter_data(
    df,
    calories_min=0,
    calories_max=None,
    difficulty="All",
    equipment_include=None,
    equipment_exclude=None,
    muscle_group="All",
):
    """
    Calorie range and excluded equipment always apply.

    Difficulty, included equipment, and muscle groups use **AND** across categories: if you
    pick muscles, the exercise must match your muscle choice; if you also pick difficulty,
    it must match that too; same for equipment include. Within each multiselect, multiple
    selections still use OR (e.g. Chest or Back).

    If a category is left empty, that category does not filter (all values allowed).
    """
    out = df.copy()
    out = out[out["Burns Calories"] >= calories_min]
    if calories_max is not None:
        out = out[out["Burns Calories"] <= calories_max]

    exc = _tokens(equipment_exclude)
    if exc:
        out = out[~_series_matches_any(out["Equipment Needed"], exc)]

    levels = _difficulty_levels(difficulty)
    inc = _tokens(equipment_include)
    muc = _tokens(muscle_group) if muscle_group not in (None, "All", "", []) else []

    combined = pd.Series(True, index=out.index)
    if levels:
        combined &= out["Difficulty Level"].isin(levels)
    if inc:
        combined &= _series_matches_any(out["Equipment Needed"], inc)
    if muc:
        combined &= _series_matches_muscles(out["Target Muscle Group"], muc)
    out = out[combined]

    return out
