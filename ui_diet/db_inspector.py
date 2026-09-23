"""UI Module presenting a dataframe grid view mapping all underlying database records."""

import streamlit as st
import pandas as pd
from backend_diet import db_core


def render_database_tables_inspector() -> None:
    """Loads all system tables directly through pandas to monitor background changes."""
    st.markdown("---")
    st.write("### 🔍 System Database Table Inspector")

    conn = db_core.get_db_connection()
    cursor = conn.cursor()
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';").fetchall()
    
    if not tables:
        conn.close()
        st.info("No tables active.")
        return

    table_names = [t[0] for t in tables]
    selected_table = st.selectbox("Select Storage Schema Layer:", options=table_names, key="diet_db_dropdown")

    if selected_table:
        try:
            data_rows = cursor.execute(f"SELECT * FROM {selected_table}").fetchall()
            column_headers = [desc[0] for desc in cursor.description]
            
            if not data_rows:
                st.info(f"Table `{selected_table}` is currently empty.")
            else:
                df = pd.DataFrame(data_rows, columns=column_headers)
                st.dataframe(df, width='stretch', key=f"df_view_{selected_table}")
        except Exception as err:
            st.error(f"Error reading layout metrics rows: {str(err)}")
            
    conn.close()
