"""
FitSense AI Dashboard - Overview Page
KPI cards and summary charts showing key metrics.
"""

import streamlit as st
import sys
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import utilities
from utils.db import execute_query, ensure_db_connection
from utils.charts import (
    create_pie_chart,
    create_bar_chart,
    create_scatter_chart,
    get_chart_config,
)
from utils.sql_console import show_sql_console
from utils.queries import (
    A6_MOST_POPULAR_GOALS,
    A7_CONDITIONS_BY_SEVERITY,
    J3_TOP_ACTIVE_USERS,
    SS1_USER_SUMMARY,
    U1_TABLE_ROW_COUNTS,
    APP_COUNT_USERS,
    APP_COUNT_WORKOUTS,
    APP_AVG_SLEEP_DURATION,
    APP_COUNT_ACTIVE_PLANS,
)
from utils.sidebar import render_sidebar

# Page configuration
st.set_page_config(
    page_title="Overview - FitSense AI Dashboard",
    page_icon="assets/logo.svg",
    layout="wide",
)

# Load CSS
css_path = project_root / "assets" / "style.css"
if css_path.exists():
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    """Main overview page."""

    # Render sidebar
    render_sidebar()

    st.markdown(
        """
    <div style="padding: 10px 0 30px 0;">
        <h1 style="color: #F1F5F9; margin: 0; font-size: 2.0rem;">📊 Overview</h1>
        <p style="color: #94A3B8; margin: 10px 0 0 0;">
            Key metrics and summary visualizations from the FitSense AI database
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Ensure database connection is established
    ensure_db_connection()

    if not st.session_state.get("db_connected", False):
        st.warning(
            "Please ensure the database is connected. Check the main page for setup instructions."
        )
        return

    try:
        # =============================================================================
        # KPI CARDS
        # =============================================================================

        st.subheader("📈 Key Metrics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            try:
                df = execute_query(APP_COUNT_USERS)
                st.metric(
                    "Total Users",
                    f"{df['cnt'].iloc[0]:,}",
                    help="Total number of registered users",
                )
            except:
                st.metric("Total Users", "—")

        with col2:
            try:
                df = execute_query(APP_COUNT_WORKOUTS)
                st.metric(
                    "Total Workouts",
                    f"{df['cnt'].iloc[0]:,}",
                    help="Total number of logged workouts",
                )
            except:
                st.metric("Total Workouts", "—")

        with col3:
            try:
                df = execute_query(APP_AVG_SLEEP_DURATION)
                avg_sleep = df["avg"].iloc[0]
                st.metric(
                    "Avg Sleep Duration",
                    f"{avg_sleep}h" if avg_sleep else "—",
                    help="Average sleep hours",
                )
            except:
                st.metric("Avg Sleep Duration", "—")

        with col4:
            try:
                df = execute_query(APP_COUNT_ACTIVE_PLANS)
                st.metric(
                    "Active Plans",
                    f"{df['cnt'].iloc[0]:,}",
                    help="Number of active workout plans",
                )
            except:
                st.metric("Active Plans", "—")

        st.divider()

        # =============================================================================
        # PIE CHARTS - GOALS AND CONDITIONS
        # =============================================================================

        st.subheader("📊 Popular Goals & Conditions")

        col1, col2 = st.columns(2)

        with col1:
            try:
                start_time = time.time()
                df = execute_query(A6_MOST_POPULAR_GOALS)
                exec_time = time.time() - start_time

                if not df.empty:
                    fig = create_pie_chart(
                        df.head(8),
                        values="total_users",
                        names="name",
                        title="Most Popular Goals",
                    )
                    st.plotly_chart(
                        fig, config=get_chart_config(), width='stretch'
                    )
                    show_sql_console(
                        A6_MOST_POPULAR_GOALS,
                        "Goal Popularity",
                        "Aggregate + INNER JOIN",
                        exec_time,
                    )
                else:
                    st.info("No goal data available")
            except Exception as e:
                st.error(f"Error loading goals data: {e}")

        with col2:
            try:
                start_time = time.time()
                df = execute_query(A7_CONDITIONS_BY_SEVERITY)
                exec_time = time.time() - start_time

                if not df.empty:
                    fig = create_pie_chart(
                        df,
                        values="total",
                        names="severity",
                        title="Condition Severity Distribution",
                    )
                    st.plotly_chart(
                        fig, config=get_chart_config(), width='stretch'
                    )
                    show_sql_console(
                        A7_CONDITIONS_BY_SEVERITY,
                        "Condition Severity",
                        "Aggregate",
                        exec_time,
                    )
                else:
                    st.info("No condition data available")
            except Exception as e:
                st.error(f"Error loading conditions data: {e}")

        st.divider()

        # =============================================================================
        # BAR CHART - TOP ACTIVE USERS
        # =============================================================================

        st.subheader("🏆 Top Active Users")

        try:
            start_time = time.time()
            df = execute_query(J3_TOP_ACTIVE_USERS)
            exec_time = time.time() - start_time

            if not df.empty:
                fig = create_bar_chart(
                    df.head(10),
                    x="name",
                    y="total_workouts",
                    title="Top 10 Most Active Users",
                )
                st.plotly_chart(
                    fig, config=get_chart_config(), width='stretch'
                )
                show_sql_console(
                    J3_TOP_ACTIVE_USERS,
                    "Top Active Users",
                    "INNER JOIN + Aggregate",
                    exec_time,
                )
            else:
                st.info("No workout data available")
        except Exception as e:
            st.error(f"Error loading active users data: {e}")

        st.divider()

        # =============================================================================
        # SCATTER PLOT - WORKOUTS VS GOALS
        # =============================================================================

        st.subheader("📈 Workouts vs Goals Correlation")

        try:
            start_time = time.time()
            df = execute_query(SS1_USER_SUMMARY)
            exec_time = time.time() - start_time

            if (
                not df.empty
                and "workout_count" in df.columns
                and "goal_count" in df.columns
            ):
                fig = create_scatter_chart(
                    df,
                    x="workout_count",
                    y="goal_count",
                    title="User Profile: Workout Count vs Goal Count",
                )
                st.plotly_chart(
                    fig, config=get_chart_config(), width='stretch'
                )
                show_sql_console(
                    SS1_USER_SUMMARY,
                    "Workouts vs Goals",
                    "Subquery in SELECT",
                    exec_time,
                )
            else:
                st.info("No user summary data available")
        except Exception as e:
            st.error(f"Error loading user summary data: {e}")

        st.divider()

        # =============================================================================
        # BAR CHART - TABLE ROW COUNTS
        # =============================================================================

        st.subheader("🗄️ Database Table Sizes")

        try:
            start_time = time.time()
            df = execute_query(U1_TABLE_ROW_COUNTS)
            exec_time = time.time() - start_time

            if not df.empty:
                fig = create_bar_chart(
                    df, x="tbl", y="cnt", title="Row Counts Across All Tables"
                )
                st.plotly_chart(
                    fig, config=get_chart_config(), width='stretch'
                )
                show_sql_console(
                    U1_TABLE_ROW_COUNTS, "Table Row Counts", "UNION ALL", exec_time
                )
            else:
                st.info("No table data available")
        except Exception as e:
            st.error(f"Error loading table counts: {e}")

        st.divider()

        # =============================================================================
        # SQL CONCEPT COVERAGE SUMMARY
        # =============================================================================

        st.subheader("📚 SQL Concepts Demonstrated on This Page")

        concepts = [
            ("A6 - Most Popular Goals", "Aggregate + INNER JOIN"),
            ("A7 - Conditions by Severity", "Aggregate"),
            ("J3 - Top Active Users", "INNER JOIN + Aggregate"),
            ("SS1 - User Summary", "Subquery in SELECT"),
            ("U1 - Table Row Counts", "UNION ALL"),
        ]

        cols = st.columns(5)
        for i, (query_id, concept) in enumerate(concepts):
            with cols[i]:
                st.markdown(
                    f"""
                <div class="fitsense-card" style="padding: 12px; text-align: center;">
                    <span style="font-size: 12px; color: #3B82F6;">{query_id}</span><br>
                    <span style="font-size: 10px; color: #94A3B8;">{concept}</span>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    except Exception as e:
        st.error(f"An error occurred while loading the overview data: {e}")
        st.info(
            "Make sure the MySQL database is running and the FitSense AI database is imported."
        )


if __name__ == "__main__":
    main()
