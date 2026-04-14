"""
FitSense AI Dashboard - Workouts Page
Workout analysis, exercise statistics, and performance metrics.
Demonstrates: Aggregate, INNER JOIN, Nested Subquery, Correlated Subquery, >= ALL
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
    create_histogram,
    create_bar_chart,
    create_scatter_chart,
    get_chart_config,
)
from utils.sql_console import show_sql_console
from utils.queries import (
    A5_WORKOUTS_PER_DAY,
    A8_AVG_WORKOUT_DURATION,
    J2_MOST_USED_EXERCISES,
    N1_USERS_ABOVE_AVERAGE_WORKOUTS,
    N2_HEAVIEST_LIFTS_ABOVE_AVG,
    C1_USERS_LAST_WORKOUT_EXCEEDED_AVG,
    E1_USER_WITH_MOST_WORKOUTS,
)
from utils.sidebar import render_sidebar

# Page configuration
st.set_page_config(
    page_title="Workouts - FitSense AI Dashboard",
    page_icon="assets/logo.svg",
    layout="wide",
)

# Load CSS
css_path = project_root / "assets" / "style.css"
if css_path.exists():
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    """Main workouts page."""

    # Render sidebar
    render_sidebar()

    st.markdown(
        """
    <div style="padding: 10px 0 30px 0;">
        <h1 style="color: #F1F5F9; margin: 0; font-size: 2.0rem;">Workouts Analytics</h1>
        <p style="color: #94A3B8; margin: 10px 0 0 0;">
            Analyze workout patterns, exercise popularity, and performance metrics
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
        # KPI HIGHLIGHTS - TOP PERFORMER BADGE
        # =============================================================================

        st.subheader("🏆 Top Performer")

        col1, col2, col3 = st.columns(3)

        with col1:
            try:
                df = execute_query(E1_USER_WITH_MOST_WORKOUTS)
                if not df.empty:
                    st.metric(
                        "Most Workouts",
                        df["name"].iloc[0],
                        delta=int(df["total"].iloc[0]),
                        help="User with the highest workout count using >= ALL",
                    )
                    show_sql_console(
                        E1_USER_WITH_MOST_WORKOUTS,
                        "Top Performer",
                        ">= ALL",
                        show=False,
                    )
            except:
                st.metric("Most Workouts", "—")

        with col2:
            try:
                df = execute_query(A8_AVG_WORKOUT_DURATION)
                if not df.empty:
                    avg_duration = df["avg_mins"].mean()
                    st.metric(
                        "Global Avg Duration",
                        f"{avg_duration:.1f} min",
                        help="Average workout duration across all users (Subquery in FROM)",
                    )
            except:
                st.metric("Global Avg Duration", "—")

        with col3:
            try:
                df = execute_query(N1_USERS_ABOVE_AVERAGE_WORKOUTS)
                st.metric(
                    "High Engagement",
                    f"{len(df)} users",
                    help="Users with above-average workout counts (Nested Subquery)",
                )
            except:
                st.metric("High Engagement", "—")

        st.divider()

        # =============================================================================
        # HISTOGRAM - WORKOUT DURATION DISTRIBUTION
        # =============================================================================

        st.subheader("📊 Workout Duration Distribution")

        try:
            start_time = time.time()
            df = execute_query(A8_AVG_WORKOUT_DURATION)
            exec_time = time.time() - start_time

            if not df.empty:
                fig = create_histogram(
                    df,
                    x="avg_mins",
                    title="Average Workout Duration Distribution (minutes)",
                    color="#F59E0B",
                    nbins=20,
                )
                fig.update_layout(
                    xaxis_title="Duration (minutes)", yaxis_title="Number of Users"
                )
                st.plotly_chart(fig, config=get_chart_config(), width="stretch")
                show_sql_console(
                    A8_AVG_WORKOUT_DURATION,
                    "Workout Duration",
                    "Aggregate + INNER JOIN",
                    exec_time,
                )
            else:
                st.info("No workout duration data available")
        except Exception as e:
            st.error(f"Error loading duration data: {e}")

        st.divider()

        # =============================================================================
        # BAR CHART - WORKOUTS PER DAY OF WEEK
        # =============================================================================

        st.subheader("📅 Workouts by Day of Week")

        try:
            start_time = time.time()
            df = execute_query(A5_WORKOUTS_PER_DAY)
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
                df["day_of_week"] = pd.Categorical(
                    df["day_of_week"], categories=day_order, ordered=True
                )
                df = df.sort_values("day_of_week")

                fig = create_bar_chart(
                    df,
                    x="day_of_week",
                    y="total",
                    title="Number of Workouts by Day of Week",
                    color_discrete_sequence=["#3B82F6"],
                )
                fig.update_layout(
                    xaxis_title="Day of Week", yaxis_title="Total Workouts"
                )
                st.plotly_chart(fig, config=get_chart_config(), width="stretch")
                show_sql_console(
                    A5_WORKOUTS_PER_DAY, "Workouts by Day", "Aggregate", exec_time
                )
            else:
                st.info("No workout day data available")
        except Exception as e:
            st.error(f"Error loading day data: {e}")

        st.divider()

        # =============================================================================
        # BAR CHART - TOP 10 EXERCISES
        # =============================================================================

        st.subheader("💪 Most Used Exercises")

        try:
            start_time = time.time()
            df = execute_query(J2_MOST_USED_EXERCISES)
            exec_time = time.time() - start_time

            if not df.empty:
                fig = create_bar_chart(
                    df,
                    x="times_programmed",
                    y="name",
                    title="Top 10 Most Used Exercises in Plans",
                    orientation="h",
                    color_discrete_sequence=["#10B981"],
                )
                fig.update_layout(
                    xaxis_title="Times Used in Plans", yaxis_title="Exercise"
                )
                st.plotly_chart(fig, config=get_chart_config(), width="stretch")
                show_sql_console(
                    J2_MOST_USED_EXERCISES,
                    "Most Used Exercises",
                    "INNER JOIN + Aggregate",
                    exec_time,
                )
            else:
                st.info("No exercise data available")
        except Exception as e:
            st.error(f"Error loading exercises data: {e}")

        st.divider()

        # =============================================================================
        # SCATTER PLOT - HEAVIEST LIFTS
        # =============================================================================

        st.subheader("🏆 Heaviest Lifts Analysis")

        try:
            start_time = time.time()
            df = execute_query(N2_HEAVIEST_LIFTS_ABOVE_AVG)
            exec_time = time.time() - start_time

            if not df.empty and len(df) > 0:
                fig = create_scatter_chart(
                    df,
                    x="reps",
                    y="weight",
                    title="Workout Sets: Weight vs Reps (Above Average)",
                    color_discrete_sequence=["#EC4899"],
                )
                fig.update_layout(xaxis_title="Reps", yaxis_title="Weight")
                st.plotly_chart(fig, config=get_chart_config(), width="stretch")
                show_sql_console(
                    N2_HEAVIEST_LIFTS_ABOVE_AVG,
                    "Heaviest Lifts",
                    "Nested Subquery",
                    exec_time,
                )
            else:
                st.info("No lift data available")
        except Exception as e:
            st.error(f"Error loading lifts data: {e}")

        st.divider()

        # =============================================================================
        # BAR CHART - USERS ABOVE AVERAGE
        # =============================================================================

        st.subheader("⭐ Users with Above-Average Workouts")

        try:
            start_time = time.time()
            df = execute_query(N1_USERS_ABOVE_AVERAGE_WORKOUTS)
            exec_time = time.time() - start_time

            if not df.empty:
                fig = create_bar_chart(
                    df,
                    x="name",
                    y="total_workouts",
                    title="Users with More Workouts Than Average",
                    color_discrete_sequence=["#8B5CF6"],
                )
                fig.update_layout(xaxis_title="User", yaxis_title="Total Workouts")
                st.plotly_chart(fig, config=get_chart_config(), width="stretch")
                show_sql_console(
                    N1_USERS_ABOVE_AVERAGE_WORKOUTS,
                    "Above Average Users",
                    "Nested Subquery",
                    exec_time,
                )
            else:
                st.info("All users have average or below-average workout counts")
        except Exception as e:
            st.error(f"Error loading user data: {e}")

        st.divider()

        # =============================================================================
        # SQL CONCEPT BADGES
        # =============================================================================

        st.subheader("📚 SQL Concepts Demonstrated")

        concepts_col1, concepts_col2, concepts_col3, concepts_col4 = st.columns(4)

        with concepts_col1:
            st.markdown(
                """
            <div style="background: rgba(16, 185, 129, 0.2); border: 1px solid #10B981; border-radius: 8px; padding: 12px; text-align: center;">
                <span style="color: #10B981; font-weight: bold;">INNER JOIN</span><br>
                <span style="color: #94A3B8; font-size: 11px;">Exercise usage, user data</span>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with concepts_col2:
            st.markdown(
                """
            <div style="background: rgba(245, 158, 11, 0.2); border: 1px solid #F59E0B; border-radius: 8px; padding: 12px; text-align: center;">
                <span style="color: #F59E0B; font-weight: bold;">Nested Subquery</span><br>
                <span style="color: #94A3B8; font-size: 11px;">Above-average comparisons</span>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with concepts_col3:
            st.markdown(
                """
            <div style="background: rgba(139, 92, 246, 0.2); border: 1px solid #8B5CF6; border-radius: 8px; padding: 12px; text-align: center;">
                <span style="color: #8B5CF6; font-weight: bold;">Correlated Subquery</span><br>
                <span style="color: #94A3B8; font-size: 11px;">Personal best tracking</span>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with concepts_col4:
            st.markdown(
                """
            <div style="background: rgba(236, 72, 153, 0.2); border: 1px solid #EC4899; border-radius: 8px; padding: 12px; text-align: center;">
                <span style="color: #EC4899; font-weight: bold;">>= ALL</span><br>
                <span style="color: #94A3B8; font-size: 11px;">Top performer identification</span>
            </div>
            """,
                unsafe_allow_html=True,
            )

    except Exception as e:
        st.error(f"An error occurred while loading workouts data: {e}")
        st.info(
            "Make sure the MySQL database is running and the FitSense AI database is imported."
        )


if __name__ == "__main__":
    import pandas as pd

    main()
