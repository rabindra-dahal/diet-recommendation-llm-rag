"""Module managing local document processing uploads to add customized macro text to the index."""

import os
import streamlit as st
from backend_diet import tracker_engine, vector_store


def process_custom_rag_uploads(client) -> None:
    """Intercepts file uploads, calls embeddings pipelines, and appends rows to database tables."""
    if "pending_diet_uploads" in st.session_state and st.session_state.pending_diet_uploads:
        uploaded_files = st.session_state.pending_diet_uploads
        del st.session_state.pending_diet_uploads
        
        with st.spinner("Analyzing profile inputs and calculating recipe index matrices..."):
            for uploaded_file in uploaded_files:
                file_text = uploaded_file.read().decode("utf-8")
                emb_res = client.models.embed_content(model="gemini-embedding-001", contents=file_text)
                tracker_engine.increment_api_counter("Embedding (Custom Diet Profile)")
                
                if emb_res.embeddings:
                    doc_title = os.path.splitext(uploaded_file.name)[0]
                    vector_store.save_recipe_to_knowledge_base(
                        name=doc_title,
                        category="Custom Guideline Asset",
                        macros="Parsed custom document specifications",
                        ingredients=file_text,
                        embedding=emb_res.embeddings[0].values
                    )
            st.toast(f"Successfully processed and indexed {len(uploaded_files)} diet files into RAG store!")
            st.rerun()


def render_uploader_widget() -> None:
    """Renders drag and drop boxes for macro configuration summaries."""
    st.markdown("---")
    st.write("### 📤 Custom Dietary Guideline & Recipe Uploader")
    uploaded_files = st.file_uploader(
        "Drop local text files or meal macros recipes:", type=["txt", "md"], accept_multiple_files=True, key="diet_rag_file_uploader"
    )
    if uploaded_files:
        if st.button("🚀 Parse & Index Diet Material", type="primary", width="stretch"):
            st.session_state.pending_diet_uploads = uploaded_files
            st.rerun()
