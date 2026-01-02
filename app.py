import streamlit as st
from dataclasses import dataclass
import pandas as pd

from player_model import Player
from engine import generate_basketball_rotations

st.set_page_config(page_title="Basketball Rotation Generator", layout="centered")

st.title("🏀 Basketball Rotation Generator")
st.write("Enter your roster and generate fair, balanced rotations.")

# -------------------------------------------------
# Session state init
# -------------------------------------------------
if "players" not in st.session_state:
    st.session_state.players = []

if "roster_df" not in st.session_state:
    st.session_state.roster_df = pd.DataFrame(
        columns=[
            "Name", "Height (in)",
            "Dribbling", "Shooting", "Passing",
            "Defense", "Athleticism",
            "Minutes Last Game",
            "Effective Skill"
        ]
    )

# -------------------------------------------------
# CSV IMPORT (NEW)
# -------------------------------------------------
st.subheader("📥 Import Roster from CSV")

uploaded_file = st.file_uploader(
    "Upload roster CSV",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [c.strip().lower() for c in df.columns]

        required = [
            "name", "height",
            "dribbling", "shooting", "passing",
            "defense", "athleticism"
        ]

        missing = [c for c in required if c not in df.columns]
        if missing:
            st.error(f"Missing required columns: {missing}")
        else:
            if "minutes_last_game" not in df.columns:
                df["minutes_last_game"] = 0

            st.session_state.players = [
                Player(
                    name=row["name"],
                    height=float(row["height"]),
                    dribbling=float(row["dribbling"]),
                    shooting=float(row["shooting"]),
                    passing=float(row["passing"]),
                    defense=float(row["defense"]),
                    athleticism=float(row["athleticism"]),
                    minutes_last_game=int(row["minutes_last_game"]),
                )
                for _, row in df.iterrows()
                if pd.notna(row["name"])
            ]

            st.success(f"Imported {len(st.session_state.players)} players.")

    except Exception as e:
        st.error(f"Failed to load CSV: {e}")

st.divider()

# -------------------------------------------------
# Manual player entry (unchanged)
# -------------------------------------------------
st.subheader("➕ Add Player Manually")

with st.form("add_player"):
    name = st.text_input("Name")
    height = st.number_input("Height (in)", 60, 90, 72)

    c1, c2, c3 = st.columns(3)
    dribbling = c1.number_input("Dribbling", 1, 10, 5)
    shooting = c2.number_input("Shooting", 1, 10, 5)
    passing = c3.number_input("Passing", 1, 10, 5)

    c4, c5 = st.columns(2)
    defense = c4.number_input("Defense", 1, 10, 5)
    athleticism = c5.number_input("Athleticism", 1, 10, 5)

    minutes_last_game = st.number_input(
        "Minutes Played Last Game", 0, 60, 0
    )

    submitted = st.form_submit_button("Add Player")

    if submitted and name:
        st.session_state.players.append(
            Player(
                name=name,
                height=height,
                dribbling=dribbling,
                shooting=shooting,
                passing=passing,
                defense=defense,
                athleticism=athleticism,
                minutes_last_game=minutes_last_game,
            )
        )

# -------------------------------------------------
# Editable roster table (unchanged, but now synced)
# -------------------------------------------------
st.subheader("Current Roster (Edit or Remove Players)")

if st.session_state.players:
    st.session_state.roster_df = pd.DataFrame(
        [{
            "Name": p.name,
            "Height (in)": p.height,
            "Dribbling": p.dribbling,
            "Shooting": p.shooting,
            "Passing": p.passing,
            "Defense": p.defense,
            "Athleticism": p.athleticism,
            "Minutes Last Game": p.minutes_last_game,
            "Effective Skill": round(p.effective_skill, 2)
        } for p in st.session_state.players]
    )

edited_df = st.data_editor(
    st.session_state.roster_df,
    disabled=["Effective Skill"],
    column_config={
        "Height (in)": st.column_config.NumberColumn(
            min_value=60,
            max_value=90,
            step=1,
        ),
        "Minutes Last Game": st.column_config.NumberColumn(
            min_value=0,
            max_value=60,
            step=1,
        ),
        "Dribbling": st.column_config.NumberColumn(
            min_value=1,
            max_value=10,
            step=1,
        ),
        "Shooting": st.column_config.NumberColumn(
            min_value=1,
            max_value=10,
            step=1,
        ),
        "Passing": st.column_config.NumberColumn(
            min_value=1,
            max_value=10,
            step=1,
        ),
        "Defense": st.column_config.NumberColumn(
            min_value=1,
            max_value=10,
            step=1,
        ),
        "Athleticism": st.column_config.NumberColumn(
            min_value=1,
            max_value=10,
            step=1,
        ),
    },
    num_rows="dynamic",
    use_container_width=True,
)

st.session_state.players = [
    Player(
        name=row["Name"],
        height=float(row["Height (in)"]),
        dribbling=float(row["Dribbling"]),
        shooting=float(row["Shooting"]),
        passing=float(row["Passing"]),
        defense=float(row["Defense"]),
        athleticism=float(row["Athleticism"]),
        minutes_last_game=int(row["Minutes Last Game"]),
    )
    for _, row in edited_df.iterrows()
    if row["Name"] != ""
]
st.session_state.roster_df = pd.DataFrame(
    [{
        "Name": p.name,
        "Height (in)": p.height,
        "Dribbling": p.dribbling,
        "Shooting": p.shooting,
        "Passing": p.passing,
        "Defense": p.defense,
        "Athleticism": p.athleticism,
        "Minutes Last Game": p.minutes_last_game,
        "Effective Skill": round(p.effective_skill, 2),
    } for p in st.session_state.players]
)

# -------------------------------------------------
# Game settings
# -------------------------------------------------
st.subheader("Game Settings")
rotation_minutes = st.number_input(
    "Rotation length (minutes)", min_value=1, max_value=10, value=5
)
total_game_minutes = st.number_input(
    "Total game minutes", min_value=30, max_value=50, value=32
)

st.subheader("🎯 Rotation Strategy")

use_custom_weights = st.checkbox(
    "Customize rotation weights (advanced)",
    value=False
)

# --- Default weights ---
DEFAULT_WEIGHTS = {
    "skill_weight": 0.7,
    "height_weight": 0.6,
    "minutes_weight": 2.5,
    "last_game_weight": 3.5,
}

if use_custom_weights:
    st.caption("Higher values = more important")

    c1, c2 = st.columns(2)
    skill_weight = c1.number_input(
        "Skill balance",
        min_value=0.0,
        max_value=5.0,
        value=DEFAULT_WEIGHTS["skill_weight"],
        step=0.1
    )
    height_weight = c2.number_input(
        "Height balance",
        min_value=0.0,
        max_value=5.0,
        value=DEFAULT_WEIGHTS["height_weight"],
        step=0.1
    )

    c3, c4 = st.columns(2)
    minutes_weight = c3.number_input(
        "Minutes THIS game fairness",
        min_value=0.0,
        max_value=5.0,
        value=DEFAULT_WEIGHTS["minutes_weight"],
        step=0.1
    )
    last_game_weight = c4.number_input(
        "Minutes LAST game fairness",
        min_value=0.0,
        max_value=5.0,
        value=DEFAULT_WEIGHTS["last_game_weight"],
        step=0.1
    )

else:
    # Lock in defaults
    skill_weight = DEFAULT_WEIGHTS["skill_weight"]
    height_weight = DEFAULT_WEIGHTS["height_weight"]
    minutes_weight = DEFAULT_WEIGHTS["minutes_weight"]
    last_game_weight = DEFAULT_WEIGHTS["last_game_weight"]

    st.info(
        "Using recommended defaults: fairness-first, coach-balanced rotations."
    )

# -------------------------------------------------
# Generate rotations
# -------------------------------------------------
if st.button("Generate Rotations"):

    if len(st.session_state.players) < 5:
        st.error("You need at least 5 players.")
    else:
        players = [
            Player(
                name=p.name,
                height=p.height,
                dribbling=p.dribbling,
                shooting=p.shooting,
                passing=p.passing,
                defense=p.defense,
                athleticism=p.athleticism,
                minutes_last_game=p.minutes_last_game,
            )
            for p in st.session_state.players
        ]

        rotations = generate_basketball_rotations(
                players,
                rotation_minutes=rotation_minutes,
                total_game_minutes=total_game_minutes,
                skill_weight=skill_weight,
                height_weight=height_weight,
                minutes_weight=minutes_weight,
                last_game_weight=last_game_weight,
            )

        # Rotation table
        st.subheader("🏀 Rotation Schedule")

        rotation_df = pd.DataFrame(
            {
                "Rotation": [f"Rotation {i+1}" for i in range(len(rotations))],
                "On Court": [", ".join(r) for r in rotations]
            }
        )

        st.dataframe(rotation_df, use_container_width=True)

        # Minutes table
        st.subheader("⏱ Minutes Played")

        minutes_df = pd.DataFrame(
            {
                "Player": [p.name for p in players],
                "Minutes to Played": [p.minutes_played for p in players],
                "Minutes Last Game": [p.minutes_last_game for p in players],
                "Effective Skill": [p.effective_skill for p in players]}
        ).sort_values("Minutes to Played", ascending=False)

        st.dataframe(minutes_df, use_container_width=True)