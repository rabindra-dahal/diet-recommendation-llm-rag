"""Module executing single transactions payload operations to seed baseline macro reference guidelines."""

import streamlit as st
from backend_diet import db_core, tracker_engine, vector_store


def seed_knowledge_base_orchestrator(client) -> None:
    """Seeds the local nutrition vector database using exactly 1 optimized API batch transaction call."""
    conn = db_core.get_db_connection()
    count = conn.cursor().execute("SELECT COUNT(*) FROM food_knowledge_base").fetchone()
    conn.close()

    if count == 0:
        with st.spinner("Seeding verified recipes database into local vector RAG layer..."):
            catalog = [
                {"name": "Mediterranean Quinoa Bowl", "cat": "Weight Loss", "macros": "420 kcal, P:22g, C:45g, F:14g", "ing": "Quinoa, cherry tomatoes, cucumbers, feta, olives, lemon dressing."},
                {"name": "High-Protein Salmon & Avocado Salad", "cat": "Keto / Low-Carb", "macros": "550 kcal, P:38g, C:8g, F:40g", "ing": "Baked salmon filet, mixed greens, avocado chunks, olive oil, walnuts."},
                {"name": "Oatmeal Muscle Building Parfait", "cat": "Mass Gain", "macros": "710 kcal, P:45g, C:85g, F:12g", "ing": "Rolled oats, whey protein blend, Greek yogurt, sliced banana, honey drizzle."}
            ]
            
            payload_texts = [f"{b['name']} {b['cat']} {b['macros']}" for b in catalog]
            emb_resp = client.models.embed_content(
                model="gemini-embedding-001", contents=payload_texts
            )
            tracker_engine.increment_api_counter("Batch Embedding (Diet Seeding)")
            
            if emb_resp.embeddings:
                for idx, b in enumerate(catalog):
                    vector_store.save_recipe_to_knowledge_base(
                        b["name"], b["cat"], b["macros"], b["ing"], emb_resp.embeddings[idx].values
                    )
        st.rerun()
