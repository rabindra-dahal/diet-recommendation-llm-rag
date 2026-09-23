"""UI Module presenting a visual framework table for purging vector index material entries."""

import streamlit as st
from backend_diet import vector_store


def render_document_inventory_table() -> None:
    """Displays structured layout card indicators mapping active vector recipe objects."""
    st.write("### 🗂️ RAG Recipe Reference Inventory Inspector")
    documents = vector_store.fetch_rag_document_inventory()

    if not documents:
        st.info("No custom meal fragments or reference profiles indexed inside the vector RAG schema layer.")
        return

    for idx, doc in enumerate(documents):
        with st.container(border=True):
            col_m, col_s, col_a = st.columns()
            with col_m:
                st.markdown(f"**🥗 {doc['title']}**")
                st.caption(f"Focus: `{doc['category']}`")
            with col_s:
                st.write(f"_{doc['summary']}_")
            with col_a:
                if st.button("🗑️ Wipe Asset", key=f"btn_wipe_diet_vector_{doc['id']}_{idx}", width="stretch"):
                    vector_store.delete_single_rag_document(doc["id"])
                    st.toast("Fitted macro index reference removed safely!")
                    st.rerun()
