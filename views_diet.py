"""Module providing presentation layer parsing to intercept generated choices with action inputs."""

import streamlit as st
from backend_diet import tracker_engine


def render_markdown_response(content: str, t_idx: int) -> None:
    """Parses structural 3rd level headers to draw dynamic quick-save meal buttons with automated macro values."""
    st.markdown(content)

    lines = content.split("\n")
    meal_blocks = []
    
    for line in lines:
        if line.strip().startswith("### 🍳"):
            # Sample: "### 🍳 Salmon Avocado Salad [P:35g, C:5g, F:20g, Kcal:340]"
            raw_header = line.replace("### 🍳", "").replace("**", "").replace("`", "").strip()
            
            if "[" in raw_header and "]" in raw_header:
                try:
                    display_name = raw_header.split("[")[0].strip()
                    macro_bracket = raw_header.split("[")[1].split("]")[0].strip() # "P:35g, C:5g, F:20g, Kcal:340"
                    
                    # Pull calories out of the token sequence string safely
                    calories = 0
                    for token in macro_bracket.replace(" ", "").split(","):
                        if token.lower().startswith("kcal:"):
                            calories = int(token.lower().split("kcal:")[1])
                            
                    # Clean up macro tags to match our exact parser layout: "P:35g, C:5g, F:20g"
                    macro_notes = ", ".join([t for t in macro_bracket.split(",") if "kcal" not in t.lower()]).strip()
                    
                    meal_blocks.append({
                        "display_name": display_name,
                        "calories": calories,
                        "notes": macro_notes,
                        "raw_bracket": macro_bracket
                    })
                except Exception:
                    continue

    if meal_blocks:
        st.caption("✨ **One-Click Automated Tracking Ledger:**")
        cols = st.columns(len(meal_blocks))
        for idx, meal in enumerate(meal_blocks):
            with cols[idx]:
                btn_key = f"auto_save_diet_btn_{t_idx}_{idx}"
                button_label = f"📥 Log: {meal['display_name']} ({meal['calories']} kcal)"
                
                # Zero manual configuration requested: Everything parses implicitly instantly
                if st.button(button_label, key=btn_key, width="stretch"):
                    tracker_engine.save_food_item_to_list(
                        food_name=meal["display_name"],
                        calories=meal["calories"],
                        notes=meal["notes"]
                    )
                    st.session_state.reading_list = tracker_engine.load_persisted_food_list()
                    st.toast(f"Logged {meal['display_name']}! {meal['notes']} has been added to your dashboard! 🚀")
                    st.rerun()
