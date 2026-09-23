"""Module handling calorie entry logs and star matching loops using dialog form overlays."""

import streamlit as st
from backend_diet import tracker_engine


@st.dialog("📝 Log Nutrient Breakdown Values")
def show_review_modal(food_data: dict, index: int) -> None:
    """Renders overlay popup panels to adjust structural macro entries without causing layout shifts."""
    st.write(f"#### Log Metrics for: {food_data['title']}")
    
    with st.form(key=f"diet_modal_form_{index}", border=False):
        current_cals = st.number_input("Recorded Calories (kcal):", min_value=0, value=int(food_data["calories"]), step=50, key=f"kcal_num_{index}")
        current_notes = st.text_area("Ingredients / Macronutrient breakdown notes:", value=food_data["notes"], key=f"kcal_txt_{index}")
        
        if st.form_submit_button("💾 Save Macro Entry", width="stretch"):
            tracker_engine.update_food_log_entry(food_data["title"], current_cals, current_notes)
            st.session_state.reading_list = tracker_engine.load_persisted_food_list()
            st.toast("Macro metrics saved successfully!")
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
