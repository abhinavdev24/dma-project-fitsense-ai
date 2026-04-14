"""
FitSense AI Dashboard - Main Entry Point
Streamlit application for FitSense AI MySQL database analysis.
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import utilities
from utils.db import test_connection, get_table_row_counts
from utils.charts import get_chart_config
from utils.sql_console import create_sql_console_manager
from utils.sidebar import render_sidebar

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="FitSense AI Dashboard",
    page_icon="assets/logo.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Apply custom CSS
def load_css():
    css_path = Path(__file__).parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css()

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

if "db_connected" not in st.session_state:
    st.session_state.db_connected = False

if "sql_console_manager" not in st.session_state:
    st.session_state.sql_console_manager = create_sql_console_manager()


# =============================================================================
# DATABASE CONNECTION CHECK
# =============================================================================


def check_db_connection():
    """Check database connection on app startup."""
    if not st.session_state.db_connected:
        with st.spinner("Connecting to database..."):
            connected = test_connection()
            st.session_state.db_connected = connected

            if not connected:
                st.error(
                    "⚠️ Could not connect to MySQL database. Please check your .env configuration."
                )
            else:
                st.success("✅ Connected to FitSense AI database")


# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================


def render_header():
    """Render the main header."""
    st.markdown(
        """
    <div style="padding: 10px 0 30px 0;">
        <h1 style="color: #F1F5F9; margin: 0;">FitSense AI Dashboard</h1>
        <p style="color: #94A3B8; margin: 10px 0 0 0;">
            Explore fitness data with interactive visualizations and SQL queries
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )


# =============================================================================
# MAIN APP
# =============================================================================


def main():
    """Main application entry point."""

    # Check database connection
    check_db_connection()

    # Render sidebar
    render_sidebar()

    # Render header
    render_header()

    # If not connected, show connection setup instructions
    if not st.session_state.db_connected:
        st.info(
            """
        ### 📋 Setup Instructions
        
        1. Copy `.env.example` to `.env`
        2. Update the database credentials in `.env`:
           - `DB_HOST=localhost`
           - `DB_PORT=3306`
           - `DB_USER=root`
           - `DB_PASSWORD=your_password`
           - `DB_NAME=fitsense_ai`
        3. Make sure MySQL is running and the database is imported
        4. Restart the application
        
        **Need to import the database?**
        ```bash
        mysql -u root -p < fitsense_ai_data_backup.sql
        ```
        """
        )
        return

    # Show quick stats
    st.subheader("Quick Stats")

    try:
        from utils.queries import (
            APP_COUNT_USERS,
            APP_COUNT_WORKOUTS,
            APP_AVG_SLEEP_DURATION,
            APP_COUNT_ACTIVE_PLANS,
        )
        from utils.db import execute_query

        # Run quick queries for stats
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            try:
                df = execute_query(APP_COUNT_USERS)
                st.metric("Total Users", f"{df['cnt'].iloc[0]:,}")
            except:
                st.metric("Total Users", "—")

        with col2:
            try:
                df = execute_query(APP_COUNT_WORKOUTS)
                st.metric("Total Workouts", f"{df['cnt'].iloc[0]:,}")
            except:
                st.metric("Total Workouts", "—")

        with col3:
            try:
                df = execute_query(APP_AVG_SLEEP_DURATION)
                avg_sleep = df["avg"].iloc[0]
                st.metric("Avg Sleep", f"{avg_sleep}h" if avg_sleep else "—")
            except:
                st.metric("Avg Sleep", "—")

        with col4:
            try:
                df = execute_query(APP_COUNT_ACTIVE_PLANS)
                st.metric("Active Plans", f"{df['cnt'].iloc[0]:,}")
            except:
                st.metric("Active Plans", "—")

        st.divider()

        # Navigation to pages
        st.subheader("Navigate to Analysis Pages")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.page_link(
                "pages/2_Workouts.py",
                label="🏋️ **Workouts Analytics**",
                width='stretch',
            )
            st.caption("Workout duration, exercise popularity, and performance metrics")

        with col2:
            st.page_link(
                "pages/6_Users.py",
                label="👥 **Users Analytics**",
                width='stretch',
            )
            st.caption("Demographics, activity levels, and user profiles")

        with col3:
            st.page_link(
                "pages/7_SQL_Explorer.py",
                label="🔍 **SQL Explorer**",
                width='stretch',
            )
            st.caption("Run custom queries and explore the database")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.page_link(
                "pages/8_NoSQL_Explorer.py",
                label="📦 **NoSQL Explorer**",
                width='stretch',
            )
            st.caption("Execute MongoDB aggregation queries and explore NoSQL data")

        with col2:
            st.page_link(
                "pages/3_Nutrition.py",
                label="🍎 **Nutrition Tracking**",
                width='stretch',
            )
            st.caption("Calorie intake, targets, and dietary analysis")

        with col2:
            st.page_link(
                "pages/4_Sleep.py",
                label="😴 **Sleep Analysis**",
                width='stretch',
            )
            st.caption("Sleep patterns and duration metrics")

        with col3:
            st.page_link(
                "pages/5_Weight.py",
                label="⚖️ **Weight Tracking**",
                width='stretch',
            )
            st.caption("Body composition and weight trends")

    except Exception as e:
        st.error(f"Error loading dashboard data: {e}")
        st.info("Navigate to any page using the sidebar to explore the data.")


if __name__ == "__main__":
    main()
