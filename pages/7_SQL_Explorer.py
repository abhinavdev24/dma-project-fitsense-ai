"""
FitSense AI Dashboard - SQL Explorer Page
==========================================
Interactive SQL query builder and executor.
"""

import streamlit as st
import sys
from pathlib import Path
import time
import sqlparse
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import utilities
from utils.db import execute_query, ensure_db_connection
from utils.queries import QUERIES, QUERY_CATEGORIES, QUERY_METADATA
from utils.charts import COLOR_PALETTE
from utils.sidebar import render_sidebar
from utils.query_validator import validate_readonly_query

# Page configuration
st.set_page_config(
    page_title="SQL Explorer - FitSense AI Dashboard",
    page_icon="assets/logo.svg",
    layout="wide",
)

# Load CSS
css_path = project_root / "assets" / "style.css"
if css_path.exists():
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def highlight_sql(sql: str) -> str:
    """Simple SQL syntax highlighting."""
    if not isinstance(sql, str):
        return str(sql)

    keywords = [
        "SELECT",
        "FROM",
        "WHERE",
        "JOIN",
        "LEFT",
        "RIGHT",
        "INNER",
        "OUTER",
        "ON",
        "AND",
        "OR",
        "GROUP",
        "BY",
        "ORDER",
        "HAVING",
        "LIMIT",
        "OFFSET",
        "INSERT",
        "UPDATE",
        "DELETE",
        "CREATE",
        "DROP",
        "ALTER",
        "SET",
        "VALUES",
        "UNION",
        "ALL",
        "AS",
        "DISTINCT",
        "COUNT",
        "SUM",
        "AVG",
        "MAX",
        "MIN",
        "ROUND",
        "DATE",
        "NOW",
        "INTERVAL",
        "DAY",
        "MONTH",
        "YEAR",
        "IFNULL",
        "CASE",
        "WHEN",
        "THEN",
        "ELSE",
        "END",
        "HEX",
        "TIMESTAMPDIFF",
        "MINUTE",
        "CURDATE",
        "DESC",
        "ASC",
        "IS",
        "NULL",
        "NOT",
        "EXISTS",
        "IN",
    ]

    # Escape HTML special characters first
    sql = sql.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    for keyword in keywords:
        sql = sql.replace(
            keyword,
            f'<span style="color: #3B82F6; font-weight: bold;">{keyword}</span>',
        )

    return sql


def format_sql(sql: str) -> str:
    """Format SQL query using sqlparse."""
    return sqlparse.format(sql, reindent=True, keyword_case="upper")


def get_query_type(sql: str) -> str:
    """Determine query type from SQL text."""
    if not isinstance(sql, str):
        return "Unknown"
    sql_upper = sql.upper()
    if "SELECT" not in sql_upper:
        return "Non-SELECT"
    if "JOIN" in sql_upper:
        return "JOIN"
    if "SUBQUERY" in sql_upper or sql_upper.count("SELECT") > 1:
        return "Subquery"
    if "GROUP BY" in sql_upper:
        return "Aggregate"
    return "Simple"


def main():
    """Main SQL Explorer page."""

    # Render sidebar
    render_sidebar()

    st.markdown(
        """
    <div style="padding: 10px 0 30px 0;">
        <h1 style="color: #F1F5F9; margin: 0; font-size: 2.0rem;">💻 SQL Explorer</h1>
        <p style="color: #94A3B8; margin: 10px 0 0 0;">
            Execute custom SQL queries and explore your data
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

    # Initialize session state
    if "sql_explorer_history" not in st.session_state:
        st.session_state.sql_explorer_history = []
    if "current_query" not in st.session_state:
        st.session_state.current_query = ""

    # Main layout - split panel
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### Query Editor")

        # Predefined queries dropdown
        st.markdown("**Load Predefined Query:**")

        # Build query options from QUERY_CATEGORIES and QUERY_METADATA
        query_options = [""]  # Empty option for custom query
        query_map = {}

        for category, query_ids in QUERY_CATEGORIES.items():
            for qid in query_ids:
                query_text = QUERIES.get(qid)
                metadata = QUERY_METADATA.get(qid)
                if query_text and metadata:
                    option = f"[{category}] {metadata.get('name', qid)}"
                    query_options.append(option)
                    query_map[option] = {
                        "query": query_text,
                        "name": metadata.get("name", qid),
                        "type": metadata.get("type", "Unknown"),
                        "page": metadata.get("page", "Unknown"),
                    }

        selected_query = st.selectbox(
            "Select a predefined query", query_options, label_visibility="collapsed"
        )

        if selected_query:
            query_data = query_map.get(selected_query, {})
            st.session_state.current_query = query_data.get("query", "")

            # Show query metadata
            if query_data:
                with st.expander("📋 Query Info", expanded=False):
                    st.markdown(f"**Name:** {query_data.get('name', 'N/A')}")
                    st.markdown(f"**Type:** {query_data.get('type', 'N/A')}")
                    st.markdown(f"**Page:** {query_data.get('page', 'N/A')}")

        # Query text area
        query_input = st.text_area(
            "SQL Query",
            value=st.session_state.current_query,
            height=200,
            placeholder="Enter your SQL query here...",
            label_visibility="collapsed",
        )

        # Update session state
        st.session_state.current_query = query_input

        # Buttons
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

        with col_btn1:
            run_button = st.button(
                "▶️ Run Query", type="primary", width='stretch'
            )

        with col_btn2:
            format_button = st.button("✨ Format SQL", width='stretch')

        with col_btn3:
            clear_button = st.button("🗑️ Clear", width='stretch')

        # Format SQL
        if format_button and query_input:
            formatted = format_sql(query_input)
            st.session_state.current_query = formatted
            st.rerun()

        # Clear
        if clear_button:
            st.session_state.current_query = ""
            st.rerun()

        # Execute query
        result_container = st.container()

        if run_button and query_input:
            query = query_input.strip()

            if query:
                # SECURITY: Validate query is read-only before execution
                is_valid, error_message = validate_readonly_query(query)
                if not is_valid:
                    st.error(f"Read-only violation: {error_message}")
                    st.info(
                        "This dashboard only supports SELECT queries for read-only data access. "
                        "Data modification queries (INSERT, UPDATE, DELETE, etc.) are not permitted."
                    )
                    return

                start_time = time.time()

                try:
                    df = execute_query(query)
                    exec_time = time.time() - start_time

                    if not df.empty:
                        st.session_state.sql_explorer_history.append(
                            {
                                "query": query,
                                "time": datetime.now().strftime("%H:%M:%S"),
                                "rows": len(df),
                            }
                        )

                        st.success(
                            f"✅ Query returned {len(df)} rows in {exec_time:.3f}s"
                        )

                        # Results table
                        st.markdown("#### Results")
                        st.dataframe(df, width='stretch', hide_index=True)

                        # Download button
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv,
                            file_name="query_results.csv",
                            mime="text/csv",
                            width='stretch',
                        )

                        # SQL Syntax highlighting
                        st.markdown("#### SQL Query")
                        highlighted = highlight_sql(query)
                        st.markdown(
                            f"<pre style='background: #1E293B; padding: 15px; border-radius: 8px; overflow-x: auto;'>{highlighted}</pre>",
                            unsafe_allow_html=True,
                        )

                        # Query type badge
                        query_type = get_query_type(query)
                        st.markdown(
                            f"""
                        <span style="background: rgba(59, 130, 246, 0.2); color: #3B82F6; padding: 4px 12px; border-radius: 20px; font-size: 12px;">
                            {query_type}
                        </span>
                        """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.info("Query returned no results.")

                except Exception as e:
                    st.error(f"❌ Query Error: {str(e)}")

        elif run_button and not query_input:
            st.warning("Please enter a SQL query first.")

    # Right panel - Query History
    with col_right:
        st.markdown("### 📜 Query History")

        if st.session_state.sql_explorer_history:
            for i, item in enumerate(
                reversed(st.session_state.sql_explorer_history[-10:])
            ):
                with st.expander(
                    f"⏱️ {item['time']} ({item['rows']} rows)", expanded=False
                ):
                    st.code(item["query"], language="sql")
        else:
            st.info("No queries executed yet.")

        st.divider()

        # SQL Reference
        st.markdown("### 📚 SQL Reference")

        st.markdown(
            """
        <div style="background: rgba(30, 41, 59, 0.5); border-radius: 8px; padding: 15px; margin-top: 15px;">
            <h4 style="color: #F1F5F9; margin-top: 0;">Read-Only Access</h4>
            <ul style="color: #94A3B8; line-height: 1.8;">
                <li><code style="color: #10B981;">SELECT</code> - Allowed (read data)</li>
                <li><span style="color: #EF4444; text-decoration: line-through;">INSERT</span> - Blocked</li>
                <li><span style="color: #EF4444; text-decoration: line-through;">UPDATE</span> - Blocked</li>
                <li><span style="color: #EF4444; text-decoration: line-through;">DELETE</span> - Blocked</li>
                <li><span style="color: #EF4444; text-decoration: line-through;">DROP</span> - Blocked</li>
            </ul>
            <p style="color: #94A3B8; margin-top: 10px; font-size: 0.85rem;">
                This dashboard is configured for read-only access to protect your data.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div style="background: rgba(30, 41, 59, 0.5); border-radius: 8px; padding: 15px; margin-top: 15px;">
            <h4 style="color: #F1F5F9; margin-top: 0;">FitSense Tables</h4>
            <ul style="color: #94A3B8; line-height: 1.8;">
                <li><code style="color: #10B981;">users</code></li>
                <li><code style="color: #10B981;">user_profiles</code></li>
                <li><code style="color: #10B981;">workouts</code></li>
                <li><code style="color: #10B981;">exercises</code></li>
                <li><code style="color: #10B981;">goals</code></li>
                <li><code style="color: #10B981;">sleep_duration_logs</code></li>
                <li><code style="color: #10B981;">calorie_intake_logs</code></li>
                <li><code style="color: #10B981;">weight_logs</code></li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    from datetime import datetime

    main()
