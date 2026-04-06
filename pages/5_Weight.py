"""
FitSense AI Dashboard - Weight Page
===================================
Analytics for weight tracking data.
"""

import streamlit as st
import pandas as pd
import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.db import execute_query, ensure_db_connection
from utils.charts import (
    create_scatter_plot,
    create_box_plot,
    create_line_chart,
    create_dataframe_table,
)
from utils.sql_console import show_sql_console
from utils.sidebar import render_sidebar
from utils.queries import (
    WEIGHT_TOTAL_LOGS,
    WEIGHT_AVG_WEIGHT,
    WEIGHT_AVG_BODY_FAT,
    WEIGHT_USERS_TRACKING,
    WEIGHT_VS_BODY_FAT_JOINED,
    WEIGHT_DISTRIBUTION_BY_SEX_JOINED,
    WEIGHT_TREND_90D,
    WEIGHT_BY_ACTIVITY_LEVEL,
    WEIGHT_BODY_FAT_RANGES,
    WEIGHT_USERS_WITH_GOALS,
)

# Page configuration
st.set_page_config(
    page_title="Weight Analytics | FitSense AI", page_icon="assets/logo.svg", layout="wide"
)

# Load CSS
css_path = project_root / "assets" / "style.css"
if css_path.exists():
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Render sidebar
render_sidebar()

# Page header
st.markdown('<h1 class="page-header">Weight Analytics</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="page-subtitle">Monitor weight changes and body composition trends</p>',
    unsafe_allow_html=True,
)

# Ensure database connection is established
ensure_db_connection()

if not st.session_state.get('db_connected', False):
    st.warning("Please ensure the database is connected. Check the main page for setup instructions.")
    st.stop()

# Main content
try:
    # KPI Row - Weight metrics
    st.subheader("📊 Weight Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        try:
            df = execute_query(WEIGHT_TOTAL_LOGS)
            total_logs = df["total_weight_logs"].iloc[0]
            st.metric("Total Weight Logs", f"{total_logs:,}")
        except:
            st.metric("Total Weight Logs", "—")

    with col2:
        try:
            df = execute_query(WEIGHT_AVG_WEIGHT)
            avg_weight = df["avg_weight"].iloc[0]
            st.metric("Average Weight", f"{avg_weight:.1f} kg")
        except:
            st.metric("Average Weight", "—")

    with col3:
        try:
            df = execute_query(WEIGHT_AVG_BODY_FAT)
            avg_body_fat = df["avg_body_fat"].iloc[0]
            st.metric("Avg Body Fat", f"{avg_body_fat:.1f}%")
        except:
            st.metric("Avg Body Fat", "—")

    with col4:
        try:
            df = execute_query(WEIGHT_USERS_TRACKING)
            users_tracking = df["users_tracking_weight"].iloc[0]
            st.metric("Users Tracking Weight", f"{users_tracking:,}")
        except:
            st.metric("Users Tracking Weight", "—")

    st.divider()

    # Weight vs Body Fat - Scatter Plot
    st.markdown("### Weight vs Body Fat Percentage")

    try:
        start_time = time.time()
        df_w5 = execute_query(WEIGHT_VS_BODY_FAT_JOINED)
        exec_time = time.time() - start_time

        if not df_w5.empty:
            fig_scatter = create_scatter_plot(
                df_w5,
                x="body_fat_percentage",
                y="weight",
                title="Weight vs Body Fat Percentage",
                x_axis_title="Body Fat %",
                y_axis_title="Weight (kg)",
                hover_data=["username", "activity_level"],
            )
            st.plotly_chart(fig_scatter, width="stretch")
            show_sql_console(WEIGHT_VS_BODY_FAT_JOINED, "Weight vs Body Fat", "INNER JOIN", exec_time)
        else:
            st.info("No weight and body fat data available for comparison.")
    except Exception as e:
        st.error(f"Error loading weight vs body fat data: {e}")

    # Weight Distribution by Sex - Box Plot
    st.markdown("### Weight Distribution by Sex")

    try:
        start_time = time.time()
        df_w6 = execute_query(WEIGHT_DISTRIBUTION_BY_SEX_JOINED)
        exec_time = time.time() - start_time

        if not df_w6.empty:
            fig_box = create_box_plot(
                df_w6,
                x="sex",
                y="weight",
                title="Weight Distribution by Sex",
                y_axis_title="Weight (kg)",
            )
            st.plotly_chart(fig_box, width="stretch")
            show_sql_console(
                WEIGHT_DISTRIBUTION_BY_SEX_JOINED, "Weight Distribution by Sex", "INNER JOIN", exec_time
            )
        else:
            st.info("No weight data available by sex.")
    except Exception as e:
        st.error(f"Error loading weight distribution data: {e}")

    # Weight Trend Over Time - Line Chart
    st.markdown("### Weight Trend Over Time")

    try:
        start_time = time.time()
        df_w7 = execute_query(WEIGHT_TREND_90D)
        exec_time = time.time() - start_time

        if not df_w7.empty:
            df_w7["date"] = pd.to_datetime(df_w7["date"])
            fig_line = create_line_chart(
                df_w7,
                x="date",
                y="avg_weight",
                title="Average Weight Trend (Last 90 Days)",
                y_axis_title="Weight (kg)",
            )
            st.plotly_chart(fig_line, width="stretch")
            show_sql_console(WEIGHT_TREND_90D, "Weight Trend Over Time", "Aggregate", exec_time)
        else:
            st.info("No recent weight tracking data available.")
    except Exception as e:
        st.error(f"Error loading weight trend data: {e}")

    # Weight by Activity Level
    st.markdown("### Weight by Activity Level")

    try:
        start_time = time.time()
        df_w8 = execute_query(WEIGHT_BY_ACTIVITY_LEVEL)
        exec_time = time.time() - start_time

        if not df_w8.empty:
            fig_bar = create_line_chart(
                df_w8,
                x="activity_level",
                y="avg_weight",
                title="Average Weight by Activity Level",
                y_axis_title="Weight (kg)",
                chart_type="bar",
            )
            st.plotly_chart(fig_bar, width="stretch")
            show_sql_console(
                WEIGHT_BY_ACTIVITY_LEVEL,
                "Weight by Activity Level",
                "INNER JOIN + Aggregate",
                exec_time,
            )
        else:
            st.info("No weight data available by activity level.")
    except Exception as e:
        st.error(f"Error loading weight by activity level data: {e}")

    # Body Fat Distribution
    st.markdown("### Body Fat Distribution")

    try:
        start_time = time.time()
        df_w9 = execute_query(WEIGHT_BODY_FAT_RANGES)
        exec_time = time.time() - start_time

        if not df_w9.empty:
            fig_pie = create_line_chart(
                df_w9,
                x="body_fat_range",
                y="count",
                title="Body Fat Distribution",
                y_axis_title="Count",
                chart_type="bar",
            )
            st.plotly_chart(fig_pie, width="stretch")
            show_sql_console(
                WEIGHT_BODY_FAT_RANGES, "Body Fat Distribution", "Aggregate + CASE", exec_time
            )
        else:
            st.info("No body fat data available.")
    except Exception as e:
        st.error(f"Error loading body fat distribution data: {e}")

    # Users with weight goals
    st.markdown("### Users with Weight Goals")

    try:
        start_time = time.time()
        df_w10 = execute_query(WEIGHT_USERS_WITH_GOALS)
        exec_time = time.time() - start_time

        if not df_w10.empty:
            fig_table = create_dataframe_table(df_w10, title="Users with Weight Goals")
            st.plotly_chart(fig_table, width="stretch")
            show_sql_console(
                WEIGHT_USERS_WITH_GOALS, "Users with Weight Goals", "INNER JOIN + Subquery", exec_time
            )
        else:
            st.info("No users with weight goals found.")
    except Exception as e:
        st.error(f"Error loading weight goals data: {e}")

except Exception as e:
    st.error(f"Error loading weight analytics: {str(e)}")
    st.info("Please check your database connection and try again.")

# Footer
st.markdown(
    """
<div class="dashboard-footer">
    <p>FitSense AI Dashboard | Weight Analytics Module</p>
</div>
""",
    unsafe_allow_html=True,
)
