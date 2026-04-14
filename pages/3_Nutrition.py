"""
FitSense AI Dashboard - Nutrition Page
======================================
Analytics for nutrition tracking data.
"""

import sys
from pathlib import Path
import time
import streamlit as st

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from utils.db import execute_query, ensure_db_connection
from utils.charts import (
    create_line_chart,
    create_bar_chart,
    create_histogram,
    get_chart_config,
)

# Import utilities
from utils.sql_console import show_sql_console
from utils.sidebar import render_sidebar
from utils.queries import (
    NUTRITION_TOTAL_LOGS,
    NUTRITION_AVG_CALORIES,
    NUTRITION_USERS_TRACKING,
    NUTRITION_USERS_WITH_TARGETS,
    NUTRITION_INTAKE_TREND_30D,
    NUTRITION_TOP_USERS_TOTAL,
    NUTRITION_TOP_USERS_AVG,
    NUTRITION_BY_DAY_OF_WEEK,
    NUTRITION_DISTRIBUTION,
    NUTRITION_RECENT_LOGS,
    NUTRITION_USER_TARGETS,
)

# Page configuration
st.set_page_config(
    page_title="Nutrition Analytics - FitSense AI Dashboard",
    page_icon="assets/logo.svg",
    layout="wide",
)

# Load CSS
css_path = project_root / "assets" / "style.css"
if css_path.exists():
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    """Main nutrition page."""

    # Render sidebar
    render_sidebar()

    st.markdown(
        """
    <div style="padding: 10px 0 30px 0;">
        <h1 style="color: #F1F5F9; margin: 0; font-size: 2.0rem;">Nutrition Analytics</h1>
        <p style="color: #94A3B8; margin: 10px 0 0 0;">
            Track and analyze calorie intake and dietary patterns
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
        # KPI HIGHLIGHTS - NUTRITION METRICS
        # =============================================================================

        st.subheader("📊 Nutrition Overview")

        col1, col2, col3, col4 = st.columns(4)

        # Total calorie logs
        with col1:
            try:
                df = execute_query(NUTRITION_TOTAL_LOGS)
                if not df.empty:
                    st.metric(
                        "Total Calorie Logs",
                        f"{df['total_logs'].iloc[0]:,}",
                        help="Total number of calorie intake logs in the system",
                    )
            except:
                st.metric("Total Calorie Logs", "—")

        # Average calories per log
        with col2:
            try:
                df = execute_query(NUTRITION_AVG_CALORIES)
                if not df.empty:
                    st.metric(
                        "Avg Calories/Log",
                        f"{df['avg_calories'].iloc[0]:,.0f}",
                        help="Average calories consumed per log entry",
                    )
            except:
                st.metric("Avg Calories/Log", "—")

        # Users tracking nutrition
        with col3:
            try:
                df = execute_query(NUTRITION_USERS_TRACKING)
                if not df.empty:
                    st.metric(
                        "Users Tracking",
                        f"{df['users_tracking'].iloc[0]:,}",
                        help="Number of users who have logged calorie intake",
                    )
            except:
                st.metric("Users Tracking", "—")

        # Users with calorie targets
        with col4:
            try:
                df = execute_query(NUTRITION_USERS_WITH_TARGETS)
                if not df.empty:
                    st.metric(
                        "Users with Targets",
                        f"{df['users_with_targets'].iloc[0]:,}",
                        help="Number of users with defined calorie targets",
                    )
            except:
                st.metric("Users with Targets", "—")

        st.divider()

        # =============================================================================
        # LINE CHART - CALORIE INTAKE OVER TIME
        # =============================================================================

        st.subheader("📈 Calorie Intake Over Time")

        try:
            start_time = time.time()
            df = execute_query(NUTRITION_INTAKE_TREND_30D)
            exec_time = time.time() - start_time

            if not df.empty:
                df["log_date"] = pd.to_datetime(df["log_date"])
                fig = create_line_chart(
                    df,
                    x="log_date",
                    y="avg_calories",
                    title="Average Calorie Intake per Log (Last 30 Days)",
                )
                fig.update_layout(
                    yaxis_title="Calories", xaxis_title="Date", height=400
                )
                st.plotly_chart(fig, config=get_chart_config(), width="stretch")
                show_sql_console(
                    NUTRITION_INTAKE_TREND_30D,
                    "Calorie Intake Trend",
                    "Aggregate + GROUP BY",
                    exec_time,
                )
            else:
                st.info("No recent calorie data available.")
        except Exception as e:
            st.error(f"Error loading calorie trend: {e}")

        st.divider()

        # =============================================================================
        # BAR CHART - TOP USERS BY CALORIES
        # =============================================================================

        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("#### 🏆 Total Calorie Totals (Top 10)")

            try:
                start_time = time.time()
                df = execute_query(NUTRITION_TOP_USERS_TOTAL)
                exec_time = time.time() - start_time

                if not df.empty:
                    fig = create_bar_chart(
                        df, x="name", y="total_calories", title="Weekly Calorie Totals"
                    )
                    st.plotly_chart(fig, config=get_chart_config(), width="stretch")
                    show_sql_console(
                        NUTRITION_TOP_USERS_TOTAL,
                        "Weekly Totals",
                        "INNER JOIN",
                        exec_time,
                    )
                else:
                    st.info("No weekly calorie data available.")
            except Exception as e:
                st.error(f"Error: {e}")

        with col_chart2:
            st.markdown("#### 📊 Top Users by Average Calorie Intake")

            try:
                start_time = time.time()
                df = execute_query(NUTRITION_TOP_USERS_AVG)
                exec_time = time.time() - start_time

                if not df.empty:
                    fig = create_bar_chart(
                        df,
                        x="name",
                        y="avg_calories",
                        title="Average Calorie Intake (Top 10)",
                        color_discrete_sequence=["#10B981"],
                    )
                    st.plotly_chart(fig, config=get_chart_config(), width="stretch")
                    show_sql_console(
                        NUTRITION_TOP_USERS_AVG,
                        "Top Users",
                        "INNER JOIN + Aggregate",
                        exec_time,
                    )
                else:
                    st.info("No user calorie data available.")
            except Exception as e:
                st.error(f"Error: {e}")

        st.divider()

        # =============================================================================
        # BAR CHART - CALORIES BY DAY OF WEEK
        # =============================================================================

        st.subheader("📅 Calorie Intake by Day of Week")

        try:
            start_time = time.time()
            df = execute_query(NUTRITION_BY_DAY_OF_WEEK)
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
                    y="avg_calories",
                    title="Average Calorie Intake by Day of Week",
                )
                fig.update_layout(
                    xaxis_title="Day of Week", yaxis_title="Average Calories"
                )
                st.plotly_chart(fig, config=get_chart_config(), width="stretch")
                show_sql_console(
                    NUTRITION_BY_DAY_OF_WEEK, "By Day of Week", "Aggregate", exec_time
                )
            else:
                st.info("No day-of-week data available.")
        except Exception as e:
            st.error(f"Error loading day-of-week data: {e}")

        st.divider()

        # =============================================================================
        # HISTOGRAM - CALORIE DISTRIBUTION
        # =============================================================================

        st.subheader("📊 Calorie Distribution")

        try:
            start_time = time.time()
            df = execute_query(NUTRITION_DISTRIBUTION)
            exec_time = time.time() - start_time

            if not df.empty:
                fig = create_histogram(
                    df,
                    x="calories_consumed",
                    title="Calorie Intake Distribution",
                    color="#F59E0B",
                    nbins=30,
                )
                fig.update_layout(xaxis_title="Calories", yaxis_title="Frequency")
                st.plotly_chart(fig, config=get_chart_config(), width="stretch")
                show_sql_console(
                    NUTRITION_DISTRIBUTION,
                    "Calorie Distribution",
                    "Simple Query",
                    exec_time,
                )
            else:
                st.info("No calorie distribution data available.")
        except Exception as e:
            st.error(f"Error loading distribution: {e}")

        st.divider()

        # =============================================================================
        # TABLE - RECENT CALORIE LOGS
        # =============================================================================

        st.subheader("📋 Recent Calorie Logs")

        try:
            start_time = time.time()
            df = execute_query(NUTRITION_RECENT_LOGS)
            exec_time = time.time() - start_time

            if not df.empty:
                df["log_date"] = pd.to_datetime(df["log_date"]).dt.strftime("%Y-%m-%d")
                st.dataframe(df, width="stretch", hide_index=True)
                show_sql_console(
                    NUTRITION_RECENT_LOGS, "Recent Logs", "INNER JOIN", exec_time
                )
            else:
                st.info("No recent calorie data available.")
        except Exception as e:
            st.error(f"Error loading logs: {e}")

        st.divider()

        # =============================================================================
        # TABLE - USER CALORIE TARGETS
        # =============================================================================

        st.subheader("🎯 User Calorie Targets")

        try:
            start_time = time.time()
            df = execute_query(NUTRITION_USER_TARGETS)
            exec_time = time.time() - start_time

            if not df.empty:
                st.dataframe(df, width="stretch", hide_index=True)
                show_sql_console(
                    NUTRITION_USER_TARGETS, "Calorie Targets", "INNER JOIN", exec_time
                )
            else:
                st.info("No calorie target data available.")
        except Exception as e:
            st.error(f"Error loading targets: {e}")

    except Exception as e:
        st.error(f"An error occurred while loading nutrition data: {e}")
        st.info(
            "Make sure the MySQL database is running and the FitSense AI database is imported."
        )


if __name__ == "__main__":
    import pandas as pd

    main()
