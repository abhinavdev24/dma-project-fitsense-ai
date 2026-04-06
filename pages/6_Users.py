"""
FitSense AI Dashboard - Users Page
User demographics, activity levels, and profile analysis.
Demonstrates: Aggregate, INNER JOIN, Correlated Subquery, Subquery in FROM, UNION
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
    create_pie_chart,
    create_scatter_chart,
    create_bar_chart,
    get_chart_config,
)
from utils.sql_console import show_sql_console
from utils.queries import (
    APP_COUNT_USERS,
    A2_USERS_BY_SEX,
    A3_AVG_HEIGHT_BY_SEX,
    A4_AGE_DISTRIBUTION,
    J1_USER_PROFILES_DEMOGRAPHICS,
    C2_USERS_WITH_MORE_GOALS_THAN_AVG,
    U2_USERS_WITH_GOALS_OR_CONDITIONS,
    SF2_ACTIVITY_LEVEL_WITH_PERCENTAGE,
    O1_USERS_WITH_NO_GOALS,
    E3_USERS_WHO_LOGGED_WEIGHT,
)
from utils.sidebar import render_sidebar

# Page configuration
st.set_page_config(
    page_title="Users - FitSense AI Dashboard",
    page_icon="assets/logo.svg",
    layout="wide",
)

# Load CSS
css_path = project_root / "assets" / "style.css"
if css_path.exists():
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    """Main users page."""

    # Render sidebar
    render_sidebar()

    st.markdown(
        """
    <div style="padding: 10px 0 30px 0;">
        <h1 style="color: #F1F5F9; margin: 0; font-size: 2.0rem;">Users Analytics</h1>
        <p style="color: #94A3B8; margin: 10px 0 0 0;">
            Demographics, activity levels, and user profile analysis
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

        st.subheader("📊 User Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            try:
                df = execute_query(APP_COUNT_USERS)
                st.metric(
                    "Total Users",
                    f"{df['cnt'].iloc[0]:,}",
                    help="Total registered users",
                )
            except:
                st.metric("Total Users", "—")

        with col2:
            try:
                df = execute_query(O1_USERS_WITH_NO_GOALS)
                st.metric(
                    "Users without Goals",
                    f"{len(df)}",
                    help="Users without any fitness goals (LEFT JOIN)",
                )
            except:
                st.metric("Users without Goals", "—")

        with col3:
            try:
                df = execute_query(E3_USERS_WHO_LOGGED_WEIGHT)
                st.metric(
                    "Users Logging Weight",
                    f"{len(df)}",
                    help="Users who have logged their weight (EXISTS)",
                )
            except:
                st.metric("Users Logging Weight", "—")

        with col4:
            try:
                df = execute_query(SF2_ACTIVITY_LEVEL_WITH_PERCENTAGE)
                if not df.empty:
                    most_common = df[df["total"] == df["total"].max()][
                        "activity_level"
                    ].iloc[0]
                    st.metric(
                        "Most Common Activity",
                        most_common,
                        help="Most common activity level (Subquery in FROM)",
                    )
            except:
                st.metric("Most Common Activity", "—")

        st.divider()

        # =============================================================================
        # PIE CHART - SEX DISTRIBUTION
        # =============================================================================

        st.subheader("📊 Sex Distribution")

        try:
            start_time = time.time()
            df = execute_query(A2_USERS_BY_SEX)
            exec_time = time.time() - start_time

            if not df.empty:
                fig = create_pie_chart(
                    df, values="total", names="sex", title="User Distribution by Sex"
                )
                st.plotly_chart(
                    fig, config=get_chart_config(), width='stretch'
                )
                show_sql_console(
                    A2_USERS_BY_SEX, "Sex Distribution", "Aggregate", exec_time
                )
            else:
                st.info("No sex distribution data available")
        except Exception as e:
            st.error(f"Error loading sex distribution: {e}")

        st.divider()

        # =============================================================================
        # PIE CHART - ACTIVITY LEVEL DISTRIBUTION
        # =============================================================================

        st.subheader("🏃 Activity Level Distribution")

        try:
            start_time = time.time()
            df = execute_query(SF2_ACTIVITY_LEVEL_WITH_PERCENTAGE)
            exec_time = time.time() - start_time

            if not df.empty:
                fig = create_pie_chart(
                    df,
                    values="total",
                    names="activity_level",
                    title="User Activity Level Distribution (with Percentages)",
                )
                st.plotly_chart(
                    fig, config=get_chart_config(), width='stretch'
                )
                show_sql_console(
                    SF2_ACTIVITY_LEVEL_WITH_PERCENTAGE,
                    "Activity Level",
                    "Subquery in FROM",
                    exec_time,
                )
            else:
                st.info("No activity level data available")
        except Exception as e:
            st.error(f"Error loading activity levels: {e}")

        st.divider()

        # =============================================================================
        # HISTOGRAM - AGE DISTRIBUTION
        # =============================================================================

        st.subheader("📈 Age Distribution")

        try:
            start_time = time.time()
            df = execute_query(A4_AGE_DISTRIBUTION)
            exec_time = time.time() - start_time

            if not df.empty:
                fig = create_histogram(
                    df, x="age_group", title="User Age Distribution", color="#3B82F6"
                )
                fig.update_layout(
                    xaxis_title="Age Group", yaxis_title="Number of Users"
                )
                st.plotly_chart(
                    fig, config=get_chart_config(), width='stretch'
                )
                show_sql_console(
                    A4_AGE_DISTRIBUTION,
                    "Age Distribution",
                    "Aggregate + CASE WHEN",
                    exec_time,
                )
            else:
                st.info("No age distribution data available")
        except Exception as e:
            st.error(f"Error loading age distribution: {e}")

        st.divider()

        # =============================================================================
        # SCATTER PLOT - AGE VS HEIGHT
        # =============================================================================

        st.subheader("📏 Age vs Height by Sex")

        try:
            start_time = time.time()
            df = execute_query(J1_USER_PROFILES_DEMOGRAPHICS)
            exec_time = time.time() - start_time

            if not df.empty and "age" in df.columns and "height_cm" in df.columns:
                # Filter out nulls and outliers
                df_filtered = df.dropna(subset=["age", "height_cm", "sex"])
                df_filtered = df_filtered[
                    (df_filtered["height_cm"] > 100)
                    & (df_filtered["height_cm"] < 250)
                    & (df_filtered["age"] > 10)
                    & (df_filtered["age"] < 100)
                ]

                if not df_filtered.empty:
                    fig = create_scatter_chart(
                        df_filtered,
                        x="age",
                        y="height_cm",
                        title="Age vs Height by Sex (INNER JOIN)",
                        color="sex",
                    )
                    fig.update_layout(
                        xaxis_title="Age (years)", yaxis_title="Height (cm)"
                    )
                    st.plotly_chart(
                        fig, config=get_chart_config(), width='stretch'
                    )
                    show_sql_console(
                        J1_USER_PROFILES_DEMOGRAPHICS,
                        "Age vs Height",
                        "INNER JOIN",
                        exec_time,
                    )
                else:
                    st.info("Insufficient data for age vs height analysis")
            else:
                st.info("No demographic data available")
        except Exception as e:
            st.error(f"Error loading demographic data: {e}")

        st.divider()

        # =============================================================================
        # BAR CHART - AVERAGE HEIGHT BY SEX
        # =============================================================================

        st.subheader("📏 Average Height by Sex")

        try:
            start_time = time.time()
            df = execute_query(A3_AVG_HEIGHT_BY_SEX)
            exec_time = time.time() - start_time

            if not df.empty:
                fig = create_bar_chart(
                    df,
                    x="sex",
                    y="avg_height",
                    title="Average Height by Sex",
                    color_discrete_sequence=["#3B82F6", "#EC4899"],
                )
                fig.update_layout(xaxis_title="Sex", yaxis_title="Average Height (cm)")
                st.plotly_chart(
                    fig, config=get_chart_config(), width='stretch'
                )
                show_sql_console(
                    A3_AVG_HEIGHT_BY_SEX, "Avg Height by Sex", "Aggregate", exec_time
                )
            else:
                st.info("No height data available")
        except Exception as e:
            st.error(f"Error loading height data: {e}")

        st.divider()

        # =============================================================================
        # BAR CHART - USERS WITH MORE GOALS THAN AVERAGE
        # =============================================================================

        st.subheader("🎯 Users with Above-Average Goal Count")

        try:
            start_time = time.time()
            df = execute_query(C2_USERS_WITH_MORE_GOALS_THAN_AVG)
            exec_time = time.time() - start_time

            if not df.empty:
                fig = create_bar_chart(
                    df,
                    x="goal_count",
                    y="name",
                    title="Users with More Goals Than Average (Correlated Subquery)",
                    orientation="h",
                    color_discrete_sequence=["#8B5CF6"],
                )
                fig.update_layout(xaxis_title="Number of Goals", yaxis_title="User")
                st.plotly_chart(
                    fig, config=get_chart_config(), width='stretch'
                )
                show_sql_console(
                    C2_USERS_WITH_MORE_GOALS_THAN_AVG,
                    "Goals Above Average",
                    "Correlated Subquery",
                    exec_time,
                )
            else:
                st.info("All users have average or below-average goal counts")
        except Exception as e:
            st.error(f"Error loading goals data: {e}")

        st.divider()

        # =============================================================================
        # SQL CONCEPT BADGES
        # =============================================================================

        st.subheader("📚 SQL Concepts Demonstrated")

        concepts_col1, concepts_col2, concepts_col3 = st.columns(3)

        with concepts_col1:
            st.markdown(
                """
            <div style="background: rgba(59, 130, 246, 0.2); border: 1px solid #3B82F6; border-radius: 8px; padding: 12px; text-align: center;">
                <span style="color: #3B82F6; font-weight: bold;">INNER JOIN</span><br>
                <span style="color: #94A3B8; font-size: 11px;">Demographic data matching</span>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with concepts_col2:
            st.markdown(
                """
            <div style="background: rgba(139, 92, 246, 0.2); border: 1px solid #8B5CF6; border-radius: 8px; padding: 12px; text-align: center;">
                <span style="color: #8B5CF6; font-weight: bold;">Correlated Subquery</span><br>
                <span style="color: #94A3B8; font-size: 11px;">Per-user goal comparison</span>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with concepts_col3:
            st.markdown(
                """
            <div style="background: rgba(245, 158, 11, 0.2); border: 1px solid #F59E0B; border-radius: 8px; padding: 12px; text-align: center;">
                <span style="color: #F59E0B; font-weight: bold;">Subquery in FROM</span><br>
                <span style="color: #94A3B8; font-size: 11px;">Percentage calculations</span>
            </div>
            """,
                unsafe_allow_html=True,
            )

    except Exception as e:
        st.error(f"An error occurred while loading users data: {e}")
        st.info(
            "Make sure the MySQL database is running and the FitSense AI database is imported."
        )


if __name__ == "__main__":
    main()
