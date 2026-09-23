"""Module providing presentation layer parsing to intercept generated choices with action inputs."""

import streamlit as st
from backend_diet import tracker_engine


def render_markdown_response(content: str, t_idx: int) -> None:
    """Parses structural 3rd level headers to draw dynamic quick-save meal buttons."""
    st.markdown(content)

    lines = content.split("\n")
    meal_items = []
    for line in lines:
        if line.strip().startswith("### 🍳"):
            raw_title = line.replace("### 🍳", "").replace("**", "").replace("`", "").strip()
            if raw_title:
                meal_items.append(raw_title)

    if meal_items:
        st.caption("✨ **Track This Meal Choice:**")
        cols = st.columns(len(meal_items))
        for idx, title in enumerate(meal_items):
            with cols[idx]:
                btn_key = f"save_diet_btn_chat_{t_idx}_{idx}"
                display_name = title.split("for").strip() if "for" in title else title
                
                if st.button(f"📥 Log: {display_name}", key=btn_key, width="stretch"):
                    tracker_engine.save_food_item_to_list(title)
                    st.session_state.reading_list = tracker_engine.load_persisted_food_list()
                    st.toast(f"Meal option saved to your daily nutrition log: {display_name}!")
                    st.rerun()
