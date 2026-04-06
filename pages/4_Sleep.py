"""
FitSense AI Dashboard - Sleep Page
===================================
Analytics for sleep tracking data.
"""

import streamlit as st
import sys
from pathlib import Path
import time
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import utilities
from utils.db import execute_query, ensure_db_connection
from utils.charts import (
    create_box_plot,
    create_line_chart,
    create_bar_chart,
    CHART_COLORS,
    get_chart_config,
)
from utils.sql_console import show_sql_console
from utils.sidebar import render_sidebar
from utils.queries import (
    SLEEP_TOTAL_LOGS,
    SLEEP_AVG_DURATION,
    SLEEP_USERS_TRACKING,
    SLEEP_USERS_WITH_TARGETS,
    SLEEP_DURATION_TREND_AGG,
    SLEEP_BY_ACTIVITY_LEVEL,
    SLEEP_BY_DAY_OF_WEEK,
    SLEEP_USERS_EXCEEDING_TARGET,
    SLEEP_USERS_NEVER_LOGGED,
    SLEEP_RECENT_LOGS,
)

# Page configuration
st.set_page_config(
    page_title="Sleep Analytics - FitSense AI Dashboard",
    page_icon="assets/logo.svg",
    layout="wide",
)

# Load CSS
css_path = project_root / "assets" / "style.css"
if css_path.exists():
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    """Main sleep page."""

    # Render sidebar
    render_sidebar()

    st.markdown(
        """
    <div style="padding: 10px 0 30px 0;">
        <h1 style="color: #F1F5F9; margin: 0; font-size: 2.0rem;">Sleep Analytics</h1>
        <p style="color: #94A3B8; margin: 10px 0 0 0;">
            Analyze sleep patterns and quality metrics
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
        # KPI HIGHLIGHTS - SLEEP METRICS
        # =============================================================================

        st.subheader("📊 Sleep Overview")

        col1, col2, col3, col4 = st.columns(4)

        # Total sleep logs
        with col1:
            try:
                df = execute_query(SLEEP_TOTAL_LOGS)
                if not df.empty:
                    st.metric(
                        "Total Sleep Logs",
                        f"{df['total_logs'].iloc[0]:,}",
                        help="Total number of sleep duration logs",
                    )
            except:
                st.metric("Total Sleep Logs", "—")

        # Average sleep hours
        with col2:
            try:
                df = execute_query(SLEEP_AVG_DURATION)
                if not df.empty:
                    st.metric(
                        "Avg Sleep Duration",
                        f"{df['avg_hours'].iloc[0]:.1f} hrs",
                        help="Average sleep duration across all logs",
                    )
            except:
                st.metric("Avg Sleep Duration", "—")

        # Users tracking sleep
        with col3:
            try:
                df = execute_query(SLEEP_USERS_TRACKING)
                if not df.empty:
                    st.metric(
                        "Users Tracking",
                        f"{df['users_tracking'].iloc[0]:,}",
                        help="Number of users who have logged sleep data",
                    )
            except:
                st.metric("Users Tracking", "—")

        # Users with sleep targets
        with col4:
            try:
                df = execute_query(SLEEP_USERS_WITH_TARGETS)
                if not df.empty:
                    st.metric(
                        "Users with Targets",
                        f"{df['users_with_targets'].iloc[0]:,}",
                        help="Number of users with defined sleep targets",
                    )
            except:
                st.metric("Users with Targets", "—")

        st.divider()

        # =============================================================================
        # LINE CHART - SLEEP DURATION TREND
        # =============================================================================

        st.subheader("📈 Sleep Duration Trend")

        try:
            start_time = time.time()
            df = execute_query(SLEEP_DURATION_TREND_AGG)
            exec_time = time.time() - start_time

            if not df.empty:
                df["log_date"] = pd.to_datetime(df["log_date"])
                fig = create_line_chart(
                    df,
                    x="log_date",
                    y="avg_sleep_hours",
                    title="Average Sleep Duration (All Available Data)",
                )
                fig.update_layout(yaxis_title="Hours", xaxis_title="Date", height=400)
                st.plotly_chart(
                    fig, config=get_chart_config(), width='stretch'
                )
                show_sql_console(
                    SLEEP_DURATION_TREND_AGG, "Sleep Duration Trend", "Aggregate + GROUP BY", exec_time
                )
            else:
                st.info("No sleep data available.")
        except Exception as e:
            st.error(f"Error loading sleep trend: {e}")

        st.divider()

        # =============================================================================
        # BOX PLOT - SLEEP BY ACTIVITY LEVEL
        # =============================================================================

        st.subheader("📊 Sleep by Activity Level")

        try:
            start_time = time.time()
            df = execute_query(SLEEP_BY_ACTIVITY_LEVEL)
            exec_time = time.time() - start_time

            if not df.empty:
                fig = create_box_plot(
                    df,
                    x="activity_level",
                    y="sleep_duration_hours",
                    title="Sleep Duration by Activity Level",
                )
                fig.update_layout(
                    xaxis_title="Activity Level", yaxis_title="Sleep Duration (Hours)"
                )
                st.plotly_chart(
                    fig, config=get_chart_config(), width='stretch'
                )
                show_sql_console(SLEEP_BY_ACTIVITY_LEVEL, "Sleep by Activity", "INNER JOIN", exec_time)
            else:
                st.info("No sleep by activity data available.")
        except Exception as e:
            st.error(f"Error loading activity data: {e}")

        st.divider()

        # =============================================================================
        # BAR CHART - AVERAGE SLEEP BY DAY OF WEEK
        # =============================================================================

        st.subheader("📅 Sleep by Day of Week")

        try:
            start_time = time.time()
            df = execute_query(SLEEP_BY_DAY_OF_WEEK)
            exec_time = time.time() - start_time

            if not df.empty:
                # Reorder days
                day_order = [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
                df["day_name"] = pd.Categorical(
                    df["day_name"], categories=day_order, ordered=True
                )
                df = df.sort_values("day_name")

                fig = create_bar_chart(
                    df,
                    x="day_name",
                    y="avg_hours",
                    title="Average Sleep by Day of Week",
                    color_discrete_sequence=["#6366F1"],
                )
                fig.update_layout(
                    xaxis_title="Day of Week", yaxis_title="Average Sleep (Hours)"
                )
                st.plotly_chart(
                    fig, config=get_chart_config(), width='stretch'
                )
                show_sql_console(SLEEP_BY_DAY_OF_WEEK, "Sleep by Day", "Aggregate", exec_time)
            else:
                st.info("No day-of-week data available.")
        except Exception as e:
            st.error(f"Error loading day-of-week data: {e}")

        st.divider()

        # =============================================================================
        # TABLE - USERS EXCEEDING SLEEP TARGET
        # =============================================================================

        st.subheader("🎯 Users Exceeding Sleep Target (> ANY)")

        try:
            start_time = time.time()
            df = execute_query(SLEEP_USERS_EXCEEDING_TARGET)
            exec_time = time.time() - start_time

            if not df.empty:
                st.dataframe(df, width='stretch', hide_index=True)
                show_sql_console(SLEEP_USERS_EXCEEDING_TARGET, "Exceeding Target", "> ANY", exec_time)
            else:
                st.info("No users exceeding sleep targets.")
        except Exception as e:
            st.error(f"Error loading target data: {e}")

        st.divider()

        # =============================================================================
        # TABLE - USERS WHO NEVER LOGGED SLEEP
        # =============================================================================

        st.subheader("⚠️ Users Who Never Logged Sleep (NOT EXISTS)")

        try:
            start_time = time.time()
            df = execute_query(SLEEP_USERS_NEVER_LOGGED)
            exec_time = time.time() - start_time

            if not df.empty:
                st.dataframe(df, width='stretch', hide_index=True)
                show_sql_console(SLEEP_USERS_NEVER_LOGGED, "Never Logged Sleep", "NOT EXISTS", exec_time)
            else:
                st.info("All users have logged sleep data.")
        except Exception as e:
            st.error(f"Error loading user data: {e}")

        st.divider()

        # =============================================================================
        # TABLE - RECENT SLEEP LOGS
        # =============================================================================

        st.subheader("📋 Recent Sleep Logs")

        try:
            start_time = time.time()
            df = execute_query(SLEEP_RECENT_LOGS)
            exec_time = time.time() - start_time

            if not df.empty:
                df["log_date"] = pd.to_datetime(df["log_date"]).dt.strftime("%Y-%m-%d")
                st.dataframe(df, width='stretch', hide_index=True)
                show_sql_console(SLEEP_RECENT_LOGS, "Recent Logs", "INNER JOIN", exec_time)
            else:
                st.info("No recent sleep data available.")
        except Exception as e:
            st.error(f"Error loading logs: {e}")

    except Exception as e:
        st.error(f"An error occurred while loading sleep data: {e}")
        st.info(
            "Make sure the MySQL database is running and the FitSense AI database is imported."
        )


if __name__ == "__main__":
    main()
