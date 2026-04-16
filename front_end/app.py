import sys
import os, datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
import pandas as pd
import bcrypt

# Add the parent directory to sys.path manually
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# set up the dataframe
# Get the absolute path to the CSV file
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
csv_path = os.path.join(BASE_DIR, "../data/processed/exercises_cleaned.csv")
progress_file = os.path.join(BASE_DIR, "../data/user/progress.csv")
users_file = os.path.join(BASE_DIR, "../data/user/users.csv")

os.makedirs(os.path.dirname(progress_file), exist_ok=True)

if not os.path.isfile(progress_file):
    pd.DataFrame(columns=["date", "weight", "steps", "sleep_time"]).to_csv(
        progress_file, index=False
    )

if not os.path.isfile(users_file):
    pd.DataFrame(columns=["email", "password"]).to_csv(users_file, index=False)

df = pd.read_csv(csv_path)
df["Burns Calories"] = pd.to_numeric(df["Burns Calories"], errors="coerce")

# ===================== AUTH SYSTEM (ADDED ONLY) =====================
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def load_users():
    return pd.read_csv(users_file)

def save_user(email, password):
    users = load_users()
    if email in users["email"].values:
        return False
    users.loc[len(users)] = [email, hash_password(password)]
    users.to_csv(users_file, index=False)
    return True

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None

from analyses.filter_data import filter_data
from analyses.nutrition_chat import chat_with_history
from analyses.nutrition_search import search_foods

# ===================== LOGIN / SIGNUP SCREEN =====================
if not st.session_state.authenticated:
    st.title("Login / Signup")

    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pw")

        if st.button("Login"):
            users = load_users()
            match = users[users["email"] == email]

            if not match.empty and check_password(password, match.iloc[0]["password"]):
                st.session_state.authenticated = True
                st.session_state.user = email
                st.rerun()
            else:
                st.error("Invalid email or password")

    with tab_signup:
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_pw")

        if st.button("Create Account"):
            if save_user(new_email, new_password):
                st.success("Account created. Please log in.")
            else:
                st.error("Email already exists")

    st.stop()

# ===================== LOGGED IN APP =====================
st.sidebar.write(f"Logged in as: {st.session_state.user}")

if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()

st.title("Personal Health Assistant")

st.subheader("Get a Personalized Plan")

st.link_button(
    "Start Fitness Survey 🚀",
    "https://docs.google.com/forms/d/e/1FAIpQLSdtK96V0z11r_DRwxdEqCclLHmwz6jk7ndTa193uyXBYyJQ8g/viewform?usp=sharing&ouid=118083238042336260263"
)

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
    with st.form("progress_form"):
        date = st.date_input("Date", value=datetime.date.today())
        weight = st.number_input("Weight (lbs)", min_value=0.0, step=0.1)
        steps = st.number_input("Total Steps", min_value=0, step=10)
        sleep_time = st.number_input("Sleep Duration (hr)", min_value=0.0, step=0.5)
        submitted = st.form_submit_button("Add Entry")

    if submitted:
        df_progress = pd.read_csv(progress_file)
        existing_dates = set(df_progress["date"])
        if date.isoformat() in existing_dates:
            st.warning(f"You already entered data for {date.strftime('%m/%d/%Y')}.")
        else:
            df_progress.loc[len(df_progress)] = [date.isoformat(), weight, steps, sleep_time]
            df_progress.to_csv(progress_file, index=False)
            st.success("Entry added!")

    df_progress = pd.read_csv(progress_file)
    df_progress["date"] = pd.to_datetime(df_progress["date"])
    df_progress = df_progress.sort_values("date").reset_index(drop=True)

    display_df = pd.DataFrame({
        "Date": df_progress["date"].dt.strftime("%m/%d/%Y"),
        "Weight (lbs)": df_progress["weight"],
        "Steps": df_progress["steps"],
        "Sleep Duration": df_progress["sleep_time"]
    })

    st.subheader("Progress Data")
    st.dataframe(display_df, use_container_width=True)

    st.markdown("**Select rows to delete:**")
    options = [
        f"{d} — {w} lbs"
        for d, w, s, t in zip(display_df["Date"], display_df["Weight (lbs)"], display_df["Steps"], display_df["Sleep Duration"])
    ]
    to_delete = st.multiselect("Entries to remove", options)

    if st.button("Delete Selected") and to_delete:
        keep_mask = [
            f"{d} — {w} lbs" not in to_delete
            for d, w in zip(display_df["Date"], display_df["Weight (lbs)"])
        ]
        df_progress = df_progress[keep_mask].reset_index(drop=True)
        df_progress.to_csv(progress_file, index=False)
        st.success(f"Deleted {len(to_delete)} entries.")

    fig, ax = plt.subplots()
    dates = df_progress["date"]
    weights = df_progress["weight"]

    ax.plot(dates, weights, marker="o")
    ax.set_xlabel("Date")
    ax.set_ylabel("Weight (lbs)")
    ax.set_title("Weight Over Time")

    ax.margins(x=0.05)
    ax.set_xticks(dates)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%Y"))

    fig.autofmt_xdate()
    st.pyplot(fig)
