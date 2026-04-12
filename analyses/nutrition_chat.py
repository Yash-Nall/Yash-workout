"""
Nutrition Q&A: Groq (free tier) or OpenAI when API keys are set; otherwise expanded
rule-based answers that reference the user's wording.
"""

from __future__ import annotations

import os
import re
from typing import Any

import requests
import streamlit as st

SYSTEM = (
    "You are a warm, knowledgeable nutrition coach. Always respond directly to what the "
    "user asked—mirror their topic and wording. Use short paragraphs and bullet points "
    "when helpful. Give practical, evidence-informed general guidance (not personal medical "
    "diagnosis). If they mention health conditions, medications, pregnancy, or eating "
    "disorders, urge them to see a clinician or registered dietitian. About 150-450 words "
    "unless they ask for something very short."
)


def _secret(name: str) -> str:
    v = (os.getenv(name) or "").strip()
    if v:
        return v
    try:
        if name in st.secrets:
            return str(st.secrets[name]).strip()
    except Exception:
        pass
    return ""


def _chat_completions(url: str, api_key: str, model: str, messages: list[dict[str, str]]) -> str:
    payload: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "system", "content": SYSTEM}, *messages],
        "max_tokens": 1024,
        "temperature": 0.65,
    }
    r = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=90,
    )
    r.raise_for_status()
    data = r.json()
    return (data["choices"][0]["message"]["content"] or "").strip()


def _groq_chat(messages: list[dict[str, str]], api_key: str) -> str:
    model = os.getenv("GROQ_CHAT_MODEL", "llama-3.3-70b-versatile")
    return _chat_completions(
        "https://api.groq.com/openai/v1/chat/completions",
        api_key,
        model,
        messages,
    )


def _openai_chat(messages: list[dict[str, str]], api_key: str) -> str:
    model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    return _chat_completions(
        "https://api.openai.com/v1/chat/completions",
        api_key,
        model,
        messages,
    )


def _tokenize(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9']+", text.lower()) if len(w) > 1}


def _matches_triggers(t: str, words: set[str], triggers: tuple[str, ...]) -> bool:
    for tr in triggers:
        tr_l = tr.lower()
        if " " in tr_l:
            if tr_l in t:
                return True
        elif tr_l in words:
            return True
    return False


# Phrases first in list win when multiple match; order roughly: specific -> general.
_TOPICS: list[tuple[tuple[str, ...], str]] = [
    (
        (
            "fat loss",
            "lose weight",
            "weight loss",
            "lose fat",
            "belly fat",
            "burn fat",
            "cutting",
            "slim down",
            "shred",
            "get lean",
        ),
        "**Fat loss** usually works best with a **modest calorie deficit** you can sustain, "
        "high **protein** (often ~1.6-2.2 g/kg for many lifters), lots of **fiber** from "
        "plants, **2-4 strength sessions/week** to keep muscle, and **7-9h sleep**. "
        "If the scale stalls ~3 weeks, tweak food or steps slightly—avoid crash dieting.",
    ),
    (
        ("muscle gain", "bulk", "hypertrophy", "build muscle", "get bigger"),
        "**Muscle gain** needs **progressive strength training**, a **small calorie surplus** "
        "for many people, **protein** on the higher side for you, and consistent **sleep**. "
        "Gains are slow—track weights on the bar and measurements, not just bodyweight.",
    ),
    (
        ("bmi", "body mass"),
        "**BMI** is only a rough screen (weight vs height). It misses muscle vs fat and "
        "where fat sits. Pair it with **waist**, **strength**, **energy**, and labs if you "
        "have them; a clinician can help interpret the full picture.",
    ),
    (
        ("calorie", "calories", "kcal", "deficit", "surplus", "tdee", "maintenance", "how much should i eat"),
        "**Calories:** maintenance depends on size, age, sex, and activity. For fat loss, "
        "try a **small deficit** (~300-500 kcal/day) and reassess weekly trends. For "
        "muscle, a **modest surplus** plus training beats huge dirty bulks. Extreme lows "
        "need medical supervision.",
    ),
    (
        ("protein", "proteins", "amino", "chicken breast", "greek yogurt"),
        "**Protein** supports muscle and fullness. Many active adults use roughly **1.2-2.0 g/kg/day** "
        "depending on goals—spread across meals. Eggs, dairy, fish, poultry, tofu, tempeh, "
        "legumes are easy wins. Kidney issues need individualized targets.",
    ),
    (
        ("keto", "ketogenic", "low carb", "low-carb"),
        "**Low carb / keto** can reduce appetite for some; it is **not required** for fat loss. "
        "If you train hard, watch energy on leg day; choose mostly whole foods either way.",
    ),
    (
        ("carb", "carbs", "carbohydrate", "pasta", "rice", "bread"),
        "**Carbs** fuel intense training and daily focus. Prefer **whole grains, fruit, "
        "starchy veg, beans** over mostly ultra-processed snacks. Many athletes do well "
        "placing more carbs **around workouts**.",
    ),
    (
        ("saturated fat", "unsaturated", "omega", "olive oil", "avocado", "trans fat"),
        "**Fats** support hormones and vitamin absorption. Emphasize **olive oil, nuts, "
        "seeds, avocado, oily fish**; keep **industrial trans fats** near zero. Balance "
        "saturated fat with the rest of your pattern—lipid labs may guide personalization.",
    ),
    (
        ("fiber", "fibre", "constipation", "bloating"),
        "**Fiber** (often **25-38 g/day** for many adults) helps digestion and steady energy. "
        "Increase **gradually** with beans, veg, fruit, whole grains—and drink fluids—to limit bloating.",
    ),
    (
        ("sugar", "sweet", "dessert", "craving", "cravings", "candy"),
        "**Sugar** in moderation is fine; the goal is not letting sweets **replace** protein, "
        "fiber, and micronutrients. If cravings spike, check **sleep, stress, and meal size** "
        "before blaming willpower.",
    ),
    (
        ("sodium", "salt", "blood pressure", "hypertension"),
        "**Sodium:** packaged and restaurant foods dominate intake—not just the salt shaker. "
        "If BP is high, cutting **processed foods** often helps most. Heavy sweaters may "
        "need more on long hot workouts.",
    ),
    (
        ("water", "hydration", "hydrate", "electrolyte", "dehydrat"),
        "**Hydration:** pale urine is a simple check. Many people land near **2-3 L/day** "
        "from drinks + food; add more with heat and long sweat sessions. **Electrolytes** "
        "help endurance over ~60-90 minutes.",
    ),
    (
        ("vitamin", "mineral", "iron", "b12", "calcium", "supplement"),
        "**Micronutrients:** prioritize **whole foods** first. **Vegans** usually supplement "
        "**B12**; some athletes track **iron** with a clinician. Avoid random mega-doses.",
    ),
    (
        ("vegan", "vegetarian", "plant-based", "plant based"),
        "**Plant-based** diets work well with **protein each meal** (tofu, tempeh, legumes, "
        "seitan, soy milk) plus **B12**; watch **iron, zinc, omega-3** if intake is low.",
    ),
    (
        ("snack", "snacks", "hungry", "hunger", "always hungry"),
        "**Hunger fixes:** try **protein + fiber** snacks (fruit + yogurt, veg + hummus). "
        "If meals are tiny or you added training, you may simply need **more food** overall.",
    ),
    (
        ("breakfast", "lunch", "dinner", "meal prep", "recipe", "what should i eat"),
        "**Meal template:** **protein** + **vegetables/fruit** + **starchy carb** + a little "
        "**fat**. Use the **Nutrition Calculator** tab to look up foods and mix and match "
        "what you enjoy.",
    ),
    (
        ("intermittent fasting", "fasting", "eating window"),
        "**Time-restricted eating** helps some people eat less; it is not magic. Avoid it "
        "if you feel faint, under-fuel training, or have a history of **disordered eating**.",
    ),
    (
        ("running", "runner", "cardio", "marathon", "jogging", "endurance"),
        "**Endurance:** **carbs** fuel long sessions; practice fueling past ~75-90 minutes. "
        "Afterward, **protein + carbs** support recovery. Hydrate to conditions.",
    ),
    (
        ("alcohol", "beer", "wine", "drinking", "drunk"),
        "**Alcohol** adds calories, hurts **sleep and recovery**, and nudges food choices. "
        "If you drink, **moderation with food** is gentler than late-night empty calories.",
    ),
    (
        ("sleep", "stress", "anxiety", "tired", "exhausted", "burnout"),
        "**Sleep and stress** change appetite and cravings. Fixing **sleep routine, daylight, "
        "protein at meals, and training load** often improves eating patterns more than "
        "perfect macros alone.",
    ),
    (
        ("allergy", "intolerance", "celiac", "gluten", "lactose"),
        "**Allergies / celiac** need confirmed diagnosis and professional guidance—avoid "
        "self-imposed strict elimination without clarity.",
    ),
    (
        ("creatine", "preworkout", "whey", "protein powder"),
        "**Creatine monohydrate** has strong evidence for many lifters. Most other powders "
        "are optional—**food and sleep** come first. Choose **third-party tested** products "
        "when possible.",
    ),
]


def _fallback_reply(text: str) -> str:
    raw = (text or "").strip()
    if not raw:
        return (
            "Ask me anything in your own words—for example: *“Is 120 g protein enough?”*, "
            "*“Snacks for late-night hunger?”*, or *“Carbs before the gym?”*"
        )

    t = raw.lower()
    words = _tokenize(t)
    hits: list[str] = []
    for triggers, block in _TOPICS:
        if _matches_triggers(t, words, triggers):
            hits.append(block)

    seen: set[str] = set()
    uniq: list[str] = []
    for h in hits:
        if h not in seen:
            seen.add(h)
            uniq.append(h)

    preview = raw[:120] + ("..." if len(raw) > 120 else "")
    lead = f"**Re:** \"{preview}\"\n\n"

    if uniq:
        body = "\n\n---\n\n".join(uniq[:2])
        if len(uniq) > 2:
            body += (
                "\n\n---\n\n_Ask a follow-up on one topic if you want more depth._"
            )
        return lead + body

    return (
        lead
        + "Here is a general framework that still applies to most goals:\n\n"
        + "- **Protein** at each meal + **plants** (fiber) most days.\n"
        + "- **Train** with weights 2-4x/week if you can; add walking.\n"
        + "- **Sleep 7-9h**; manage stress—both change hunger.\n"
        + "- Adjust **portions** every few weeks based on weight/trend and performance.\n\n"
        + "For answers that feel like a real conversation, add a free **GROQ_API_KEY** "
        "(groq.com) or **OPENAI_API_KEY** to `.streamlit/secrets.toml`."
    )


def chat_with_history(chat_messages: list[dict[str, str]]) -> str:
    if not chat_messages or chat_messages[-1]["role"] != "user":
        return ""

    api_msgs = [
        {"role": m["role"], "content": m["content"]}
        for m in chat_messages
        if m["role"] in ("user", "assistant") and (m.get("content") or "").strip()
    ]
    last_user = api_msgs[-1]["content"].strip()
    tail = api_msgs[-12:] if len(api_msgs) > 12 else api_msgs

    groq = _secret("GROQ_API_KEY")
    if groq:
        try:
            return _groq_chat(tail, groq)
        except Exception:
            pass

    oai = _secret("OPENAI_API_KEY")
    if oai:
        try:
            return _openai_chat(tail, oai)
        except Exception as exc:
            return (
                f"_The AI service returned an error ({exc}). Here is offline guidance:_\n\n"
                + _fallback_reply(last_user)
            )

    return _fallback_reply(last_user)
