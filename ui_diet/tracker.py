"""Module handling calorie entry logs and star matching loops using dialog form overlays."""

import streamlit as st
from backend_diet import tracker_engine


@st.dialog("📝 Log Nutrient Breakdown Values")
def show_review_modal(food_data: dict, index: int) -> None:
    """Renders overlay popup panels to adjust structural macro entries with automated proportional re-scaling."""
    st.write(f"#### Log Metrics for: {food_data['title']}")
    
    # 1. Pre-parse current macro metrics values out of the notes field
    old_cals = max(1, int(food_data["calories"]))
    old_p, old_c, old_f = 0, 0, 0
    
    try:
        parts = food_data["notes"].replace(" ", "").split(",")
        for part in parts:
            if part.startswith("P:") and "g" in part:
                old_p = int(part.split("P:")[1].split("g")[0])
            elif part.startswith("C:") and "g" in part:
                old_c = int(part.split("C:")[1].split("g")[0])
            elif part.startswith("F:") and "g" in part:
                old_f = int(part.split("F:")[1].split("g")[0])
    except Exception:
        pass

    with st.form(key=f"diet_modal_form_{index}", border=False):
        # User modifies the total calorie input field
        current_cals = st.number_input(
            "Recorded Calories (kcal):", 
            min_value=0, 
            value=old_cals, 
            step=50, 
            key=f"kcal_num_{index}"
        )
        
        st.markdown(f"**Current Macro Baseline:** P: {old_p}g | C: {old_c}g | F: {old_f}g")
        st.caption("💡 Changing the calories above will automatically re-scale these grams proportionally upon saving.")
        
        if st.form_submit_button("💾 Save Macro Entry", width="stretch"):
            # 2. AUTOMATED PROPORTIONAL RE-SCALING LOGIC
            # Calculate the proportional difference multiplier ratio
            scale_ratio = current_cals / old_cals
            
            new_p = round(old_p * scale_ratio)
            new_c = round(old_c * scale_ratio)
            new_f = round(old_f * scale_ratio)
            
            # Format back into the standard parseable token string sequence
            updated_notes = f"P:{new_p}g, C:{new_c}g, F:{new_f}g"
            
            # Persist values straight down to the database layers
            tracker_engine.update_food_log_entry(food_data["title"], current_cals, updated_notes)
            st.session_state.reading_list = tracker_engine.load_persisted_food_list()
            st.toast(f"Recalculated macros to: {updated_notes}! 🚀")
            st.rerun()


def render_compact_tracker() -> None:
    """Displays user saved food lists alongside KPI summaries scorecard blocks."""
    metrics = tracker_engine.fetch_kpi_summary_metrics()
    
    st.write("### 📊 My Nutritional Analytics Dashboard")
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    
    with col_kpi1:
        st.metric(label="🍽️ Total Logged Items", value=f"{metrics['total_saved']} items")
    with col_kpi2:
        st.metric(label="🔥 Current Calorie Count", value=f"{metrics['total_calories']} kcal consumed")
    with col_kpi3:
        st.metric(label="📝 Detailed Food Logs", value=f"{metrics['completed_reviews']} meals mapped")
        
    st.markdown("---")
    st.write("### 🥗 Daily Ingestion History & Macro Checks")
    
    if not st.session_state.reading_list:
        st.info("Your logging sheet is empty. Interact with the chat engine and click log to record options here!")
        return

    c_list, c_acts = st.columns(2)
    with c_list:
        for idx, food in enumerate(st.session_state.reading_list):
            cal_lbl = f"{food['calories']} kcal" if food["calories"] > 0 else "Unmeasured cals"
            col_lbl, col_btn = st.columns(2)
            with col_lbl:
                st.write(f"**{food['title']}** — `{cal_lbl}`")
            with col_btn:
                if st.button("✏️ Edit Macro", key=f"btn_edit_diet_row_{idx}", width="stretch"):
                    show_review_modal(food, idx)
                    
    with c_acts:
        txt_export = "MY COMPILING HEALTH LOG:\n\n"
        for f in st.session_state.reading_list:
            txt_export += f"- {f['title']}\n  Energy footprint: {f['calories']} kcal\n  Notes: {f['notes']}\n\n"

        st.download_button("📥 Export Health Ledger", data=txt_export, file_name="nutrition_history_log.txt", mime="text/plain", width="stretch", key="dl_diet_logs_btn")
        if st.button("🗑️ Wipe Tracker Sheet", width="stretch", key="clear_all_diet_logs_btn"):
            tracker_engine.delete_all_logged_foods()
            st.session_state.reading_list = []
            st.rerun()
