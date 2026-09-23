"""Main layout runner keeping visual footprint tiny and well-distributed."""

import os
from dotenv import load_dotenv
from google import genai
import streamlit as st

import charts_diet
from backend_diet import db_core, tracker_engine
from ui_diet import seeder, uploader, tracker, chat_loop, inventory, db_inspector

load_dotenv()
if not os.getenv("GEMINI_API_KEY"):
    st.error("Missing GEMINI_API_KEY inside your .env file!")
    st.stop()

# Initialize localized database schema tables cleanly on boot
db_core.init_db()


@st.cache_resource
def get_gemini_client() -> genai.Client:
    """Instantiates official GenAI API network hooks."""
    return genai.Client()


client = get_gemini_client()
st.set_page_config(page_title="GenAI Diet Architect", page_icon="🥗", layout="wide")

# Seed baseline recipes into local vector space on first boot
seeder.seed_knowledge_base_orchestrator(client)

if "book_messages" not in st.session_state:
    from backend_diet import chat_history
    st.session_state.book_messages = chat_history.load_persisted_chat()
if "reading_list" not in st.session_state:
    st.session_state.reading_list = tracker_engine.load_persisted_food_list()

# --- SIDEBAR: HEALTH METRICS CONTROL PANEL ---
with st.sidebar:
    st.title("⚙️ Health Control")
    st.metric(label="🔑 Gemini API Calls", value=f"{tracker_engine.get_total_api_calls()} calls")
    st.markdown("---")
    
    # ─── NEW: SIDEBAR WATER TRACKER WIDGET ───
    st.write("💧 **Live Hydration Log**")
    current_water = tracker_engine.get_daily_hydration_total()
    st.metric(label="Daily Intake Total", value=f"{current_water} ml / 2500 ml")
    
    # Render quick adjustment buttons horizontally
    c_w1, c_w2 = st.columns(2)
    with c_w1:
        if st.button("➕ 250ml", key="btn_add_water_250", width="stretch"):
            tracker_engine.log_water_intake(250)
            st.toast("Logged 250ml water! 🥤")
            st.rerun()
    with c_w2:
        if st.button("➕ 500ml", key="btn_add_water_500", width="stretch"):
            tracker_engine.log_water_intake(500)
            st.toast("Logged 500ml water! 🫙")
            st.rerun()
            
    st.markdown("---")
    active_program = st.selectbox("Target Dietary Focus Strategy:", ["Weight Loss", "Keto / Low-Carb", "Mass Gain", "High-Protein / Athletic", "Heart-Healthy Balanced"])

    st.markdown("---")
    # ─── FIXED: ADDED UNIQUE KEY SIGNATURE TO PREVENT CLASHES ───
    active_program = st.selectbox(
        "Target Dietary Focus Strategy:", 
        ["Weight Loss", "Keto / Low-Carb", "Mass Gain", "High-Protein / Athletic", "Heart-Healthy Balanced"],
        key="sidebar_dietary_strategy_select"
    )
    
    restrictions = st.multiselect(
        "Allergies & Element Restrictions:", 
        ["Gluten-Free", "Dairy-Free", "Nut-Free", "Vegan", "Soy-Free"],
        key="sidebar_allergies_restrictions_multiselect" # Also fixed for consistency
    )

    daily_kcal_cap = st.slider("Daily Calorie Intake Limit Target (kcal):", 1200, 4500, 2000, 50)
    st.markdown("---")
    
    if st.button("🚨 Reset Profile Session", type="primary", width="stretch"):
        tracker_engine.clear_entire_session()
        st.session_state.book_messages = []
        st.session_state.reading_list = []
        if "diet_chat" in st.session_state:
            del st.session_state.diet_chat
        st.rerun()

# --- MAIN ASSISTANT CANVAS SPACES ---
st.title("🥗 Your GenAI Diet & Nutrition Companion")
st.caption("Powered by **Gemini 3.6** Direct Chat Session Architecture with Vector RAG Indices")

tab_chat, tab_logs = st.tabs(["💬 Dynamic Nutrition Chat", "📊 My Macro Logs & Tracker"])

with tab_logs:
    uploader.process_custom_rag_uploads(client)
    
    metrics = tracker_engine.fetch_kpi_summary_metrics()
    charts_diet.render_analytics_dashboard(
        analytics_logs=tracker_engine.fetch_analytics_logs(),
        caloric_target=daily_kcal_cap,
        completed_count=metrics["total_calories"]
    )
    
    tracker.render_compact_tracker()
    uploader.render_uploader_widget()
    inventory.render_document_inventory_table()
    db_inspector.render_database_tables_inspector()

with tab_chat:
    chat_loop.render_chat_interaction_loop(
        client=client,
        active_program=active_program,
        restrictions=restrictions,
        daily_kcal_cap=daily_kcal_cap
    )
