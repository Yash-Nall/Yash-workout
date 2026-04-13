import sys
import os, datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
import pandas as pd



# Add the parent directory to sys.path manually
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# set up the dataframe
# Get the absolute path to the CSV file
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
csv_path = os.path.join(BASE_DIR, "../data/processed/exercises_cleaned.csv")
progress_file = os.path.join(BASE_DIR, "../data/user/progress.csv")
os.makedirs(os.path.dirname(progress_file), exist_ok=True)
if not os.path.isfile(progress_file):
    pd.DataFrame(columns=["date", "weight", "steps", "sleep_time"]).to_csv(
        progress_file, index=False
    )
df = pd.read_csv(csv_path)


df["Burns Calories"] = pd.to_numeric(df["Burns Calories"], errors="coerce")

from analyses.filter_data import filter_data
from analyses.nutrition_chat import chat_with_history
from analyses.nutrition_search import search_foods

st.title("Personal Health Assistant")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Workout Finder", "Calorie Chatbot", "Nutrition Calculator", "Personal Tracker"]
)

with tab1:
    st.header("Exercise Recommender")
    equipment_options = sorted(
        [
            "Parallel Bars",
            "Chairs",
            "Pull-up Bar",
            "Dumbbell",
            "Barbell",
            "Bench",
            "Platform",
            "Kettlebell",
            "Step",
            "Box",
            "Resistance Band",
            "Cable Machine",
            "Low Bar",
            "TRX",
            "Wall",
            "Sturdy Surface",
        ]
    )

    muscle_group_options = sorted(
        [
            "Triceps",
            "Chest",
            "Back",
            "Biceps",
            "Core",
            "Obliques",
            "Hamstrings",
            "Glutes",
            "Quadriceps",
            "Rear Deltoids",
            "Upper Back",
            "Shoulders",
            "Calves",
            "Forearms",
            "Full Core",
            "Full Body",
            "Legs",
            "Upper Chest",
            "Lower Chest",
        ]
    )

    calories_min = st.slider("Minimum calories burned", 10, 1000, 100)
    calories_max = st.slider("Maximum calories burned", 10, 1000, 1000)
    difficulty = st.multiselect(
        "Select Difficulty Level(s)",
        ["Beginner", "Intermediate", "Advanced"],
        help="Leave empty for any difficulty. If set, exercises must match one of the levels you pick.",
    )
    equipment_include = st.multiselect(
        "Include Equipment",
        equipment_options,
        help="Leave empty for any equipment. If set, exercise equipment must mention at least one item you pick.",
    )
    equipment_exclude = st.multiselect(
        "Exclude Equipment",
        equipment_options,
        help="Hide exercises whose equipment mentions any of these.",
    )
    muscle_group = st.multiselect(
        "Select Muscle Group(s)",
        muscle_group_options,
        help="Leave empty for any muscle group. Matches **whole muscle names** in the list (e.g. Chest matches Upper/Lower Chest, not Shoulders). Multiple selections use OR.",
    )

    st.caption(
        "Filters combine with **AND**: e.g. Intermediate + Back shows only exercises that are "
        "Intermediate **and** hit a selected muscle. Within each list, choices use **OR**. "
        "Calorie sliders and excluded equipment always apply."
    )

    if st.button("Find Workouts"):
        results = filter_data(
            df,
            int(calories_min),
            int(calories_max),
            difficulty or "All",
            equipment_include or None,
            equipment_exclude or None,
            muscle_group or "All",
        )
        if not results.empty:
            st.write("Recommended Workouts:")
            st.dataframe(results)
        else:
            st.warning("No workouts found for the selected criteria. Try adjusting the filters!")

with tab2:
    st.header("Calorie Chatbot")
    st.caption(
        "Optional API keys in `.streamlit/secrets.toml`: **GROQ_API_KEY** (free at groq.com, recommended) "
        "or **OPENAI_API_KEY**. Without keys you still get expanded offline answers."
    )
    if "nutrition_chat" not in st.session_state:
        st.session_state.nutrition_chat = []

    if st.button("Clear conversation", key="clear_nutrition_chat"):
        st.session_state.nutrition_chat = []
        st.rerun()

    for msg in st.session_state.nutrition_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about nutrition, calories, or diet..."):
        st.session_state.nutrition_chat.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = chat_with_history(st.session_state.nutrition_chat)
            st.markdown(answer)
        st.session_state.nutrition_chat.append({"role": "assistant", "content": answer})

with tab3:
    st.header("Nutrition Calculator")
    st.caption(
        "Data from **Open Food Facts** (community-sourced). Results are ranked so names closer to "
        "your search appear first. Optional: valid **FATSECRET_KEY** / **FATSECRET_SECRET** if OFF is empty."
    )

    food_query = st.text_input("Enter a food name to search:", key="food_query")
    if st.button("Search Foods", key="search"):
        q = (food_query or "").strip()
        if not q:
            st.warning("Type a food name before searching.")
        else:
            try:
                st.session_state.results = search_foods(q)
                st.session_state.page_index = 0
                st.session_state.query = q
                st.session_state.nutrition_search_error = None
            except Exception as exc:
                st.session_state.results = []
                st.session_state.query = q
                st.session_state.nutrition_search_error = str(exc)
    if st.session_state.get("nutrition_search_error"):
        st.error(st.session_state["nutrition_search_error"])

    if "results" in st.session_state and st.session_state.results:
        st.subheader(f'Search results for “{st.session_state.query}”')
        results = st.session_state.results
        total = len(results)
        PAGE_SIZE = 6
        num_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)

        if "page_index" not in st.session_state:
            st.session_state.page_index = 0

        prev_col, mid_col, next_col = st.columns([1, 2, 1])
        with prev_col:
            if st.button("← Previous", key="prev") and st.session_state.page_index > 0:
                st.session_state.page_index -= 1
        with mid_col:
            st.write(f"Page {st.session_state.page_index + 1} of {num_pages} ({total} items)")
        with next_col:
            if st.button("Next →", key="next") and st.session_state.page_index < num_pages - 1:
                st.session_state.page_index += 1

        start = st.session_state.page_index * PAGE_SIZE
        end = start + PAGE_SIZE
        page_results = results[start:end]

        table_rows = []
        for food in page_results:
            name = food.get("food_name") or "Unknown"
            url = food.get("food_url") or "#"
            brand = food.get("brand") or ""
            serv = food.get("serving_label") or ""
            kc = food.get("calories")
            fg = food.get("fat_g")
            cg = food.get("carbs_g")
            pg = food.get("protein_g")

            if kc is None and food.get("food_description"):
                info_string = food.get("food_description") or ""
                if " - " in info_string:
                    _, macros_part = info_string.split(" - ", 1)
                else:
                    macros_part = info_string
                macros = {}
                for chunk in macros_part.split("|"):
                    if ":" in chunk:
                        lab, val = chunk.split(":", 1)
                        macros[lab.strip()] = val.strip()
                cal_s = macros.get("Calories", "—")
                if isinstance(cal_s, str) and cal_s.endswith("kcal"):
                    cal_s = cal_s.replace("kcal", "").strip()
                fat_s = macros.get("Fat", "—")
                carb_s = macros.get("Carbs", "—")
                prot_s = macros.get("Protein", "—")
            else:
                cal_s = f"{kc:.0f}" if kc is not None else "—"
                fat_s = f"{fg:g} g" if fg is not None else "—"
                carb_s = f"{cg:g} g" if cg is not None else "—"
                prot_s = f"{pg:g} g" if pg is not None else "—"

            table_rows.append(
                {
                    "Product": name,
                    "Brand": brand or "—",
                    "Serving": serv or "—",
                    "Calories": cal_s,
                    "Fat": fat_s,
                    "Carbs": carb_s,
                    "Protein": prot_s,
                    "Link": url,
                }
            )

        st.dataframe(
            pd.DataFrame(table_rows),
            column_config={
                "Link": st.column_config.LinkColumn("Details", display_text="Open"),
            },
            hide_index=True,
            use_container_width=True,
        )

        with st.expander("Photos for this page", expanded=False):
            cols = st.columns(3)
            for i, food in enumerate(page_results):
                img = (food.get("image_url") or "").strip()
                with cols[i % 3]:
                    if img:
                        st.image(img, use_container_width=True)
                    else:
                        st.caption("No image")
                    st.caption(food.get("food_name") or "—")

        st.markdown("---")

    elif "results" in st.session_state and st.session_state.get("query"):
        st.info(
            "No foods found for that search. Try a shorter or simpler name "
            "(e.g. “banana”, “oats”, “chicken breast”), or check your internet connection."
        )

with tab4:
    st.header("Personal Tracker")
    # — New Entry Form —
    with st.form("progress_form"):
        date = st.date_input("Date", value=datetime.date.today())
        weight = st.number_input("Weight (lbs)", min_value=0.0, step=0.1)
        steps = st.number_input("Total Steps", min_value=0, step=10)
        sleep_time = st.number_input("Sleep Duration (hr)", min_value=0.0, step=0.5)
        submitted = st.form_submit_button("Add Entry")

    if submitted:
        # Load existing entries
        df_progress = pd.read_csv(progress_file)
        # Check for duplicate date
        existing_dates = set(df_progress["date"])
        if date.isoformat() in existing_dates:
            st.warning(f"You already entered data for {date.strftime('%m/%d/%Y')}.")
        else:
            # Append new entry
            df_progress.loc[len(df_progress)] = [date.isoformat(), weight, steps, sleep_time]
            df_progress.to_csv(progress_file, index=False)
            st.success("Entry added!")

     # ─ load and prepare data ─────────────────────────────────────────────────
    df_progress = pd.read_csv(progress_file)
    df_progress["date"] = pd.to_datetime(df_progress["date"])
    df_progress = df_progress.sort_values("date").reset_index(drop=True)

     # — Prepare Display DataFrame —
    display_df = pd.DataFrame({
        "Date": df_progress["date"].dt.strftime("%m/%d/%Y"),
        "Weight (lbs)": df_progress["weight"],
        "Steps": df_progress["steps"],
        "Sleep Duration": df_progress["sleep_time"]
    })

    st.subheader("Progress Data")
    st.dataframe(display_df, use_container_width=True)

    # — Inline Deletion Controls —
    st.markdown("**Select rows to delete:**")
    # Build options by zipping the two series
    options = [
        f"{d} — {w} lbs"
        for d, w, s, t in zip(display_df["Date"], display_df["Weight (lbs)"], display_df["Steps"], display_df["Sleep Duration"])
    ]
    to_delete = st.multiselect("Entries to remove", options)

    if st.button("Delete Selected") and to_delete:
        # Construct a boolean mask: keep rows whose label is NOT in to_delete
        keep_mask = [
            f"{d} — {w} lbs" not in to_delete
            for d, w in zip(display_df["Date"], display_df["Weight (lbs)"])
        ]
        # Apply mask to original df_progress
        df_progress = df_progress[keep_mask].reset_index(drop=True)
        df_progress.to_csv(progress_file, index=False)
        st.success(f"Deleted {len(to_delete)} entr{'y' if len(to_delete)==1 else 'ies'}.")

        # Reload and re-display
        df_progress["date"] = pd.to_datetime(df_progress["date"])
        df_progress = df_progress.sort_values("date").reset_index(drop=True)
        display_df = pd.DataFrame({
            "Date": df_progress["date"].dt.strftime("%m/%d/%Y"),
            "Weight (lbs)": df_progress["weight"],
            "Steps": df_progress["steps"],
            "Sleep Duration": df_progress["sleep_time"]
        })
        st.dataframe(display_df, use_container_width=True)

    # — Plot Weight Over Time —
    fig, ax = plt.subplots()
    dates = df_progress["date"]
    weights = df_progress["weight"]

    ax.plot(dates, weights, marker="o")
    ax.set_xlabel("Date")
    ax.set_ylabel("Weight (lbs)")
    ax.set_title("Weight Over Time")

    # 1 day margin on each end
    ax.margins(x=0.05)

    # Tick exactly at each date
    ax.set_xticks(dates)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%Y"))

    # Rotate for readability
    fig.autofmt_xdate()

    st.pyplot(fig)
