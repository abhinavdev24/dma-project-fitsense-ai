"""
FitSense AI Dashboard - Shared Sidebar Module
==============================================
Common sidebar navigation used across all pages.
"""

import streamlit as st
from pathlib import Path


def render_sidebar():
    """Render the sidebar with navigation and database status."""
    with st.sidebar:
        # Logo
        logo_path = Path(__file__).parent.parent / "assets" / "logo_text.svg"
        st.image(str(logo_path), width=220)

        st.divider()

        # Navigation
        st.page_link("app.py", label="Overview", icon="🏠")
        st.page_link("pages/2_Workouts.py", label="Workouts", icon="🏋️")
        st.page_link("pages/3_Nutrition.py", label="Nutrition", icon="🍎")
        st.page_link("pages/4_Sleep.py", label="Sleep", icon="😴")
        st.page_link("pages/5_Weight.py", label="Weight", icon="⚖️")
        st.page_link("pages/6_Users.py", label="Users", icon="👥")
        st.page_link("pages/7_SQL_Explorer.py", label="SQL Explorer", icon="🔍")
        st.page_link("pages/8_NoSQL_Explorer.py", label="NoSQL Explorer", icon="📦")

        st.divider()

        # Database status - ensure connection is established first
        from utils.db import ensure_db_connection
        ensure_db_connection()
        
        db_connected = st.session_state.get("db_connected", False)
        if db_connected:
            st.success("🟢 Database Connected")
        else:
            st.error("🔴 Database Disconnected")

        # Table counts summary
        st.divider()
        st.caption("📊 Database Tables")

        try:
            if db_connected:
                from utils.db import get_table_row_counts

                table_counts = get_table_row_counts()
                total_tables = len(table_counts)
                total_rows = sum(table_counts.values())

                st.caption(f"Tables: {total_tables}")
                st.caption(f"Total Rows: {table_counts.get('users', 0):,}")
        except Exception:
            st.caption("Unable to load table info")
