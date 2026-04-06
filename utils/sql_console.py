"""
SQL Console Component for FitSense AI Dashboard
Displays executed SQL queries with syntax highlighting and type badges.
"""

import streamlit as st
import time
from datetime import datetime
from typing import Optional, Dict, Any
import re


# SQL keyword patterns for syntax highlighting
SQL_KEYWORDS = [
    'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'IN', 'EXISTS', 'BETWEEN',
    'LIKE', 'IS', 'NULL', 'AS', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'OUTER',
    'FULL', 'CROSS', 'ON', 'USING', 'GROUP', 'BY', 'HAVING', 'ORDER',
    'ASC', 'DESC', 'LIMIT', 'OFFSET', 'UNION', 'ALL', 'INTERSECT', 'EXCEPT',
    'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE', 'CREATE',
    'TABLE', 'DROP', 'ALTER', 'INDEX', 'VIEW', 'PRIMARY', 'KEY', 'FOREIGN',
    'REFERENCES', 'CASCADE', 'DISTINCT', 'COUNT', 'SUM', 'AVG', 'MIN',
    'MAX', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'CAST', 'CONVERT',
    'TIMESTAMPDIFF', 'YEAR', 'MONTH', 'DAY', 'HOUR', 'MINUTE', 'SECOND',
    'DATE', 'NOW', 'CURDATE', 'IFNULL', 'COALESCE', 'ROUND', 'HEX', 'HEX'
]

SQL_FUNCTIONS = [
    'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'ROUND', 'TIMESTAMPDIFF',
    'DAYOFWEEK', 'DAYNAME', 'TIMESTAMPDIFF', 'IFNULL', 'COALESCE'
]


def highlight_sql(query: str) -> str:
    """
    Apply syntax highlighting to SQL query.
    Returns HTML string with colored keywords.
    """
    # Escape HTML first
    query = query.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Highlight strings (quoted values)
    query = re.sub(r"('[^']*')", r"<span class='sql-string'>\1</span>", query)
    
    # Highlight numbers
    query = re.sub(r'\b(\d+\.?\d*)\b', r"<span class='sql-number'>\1</span>", query)
    
    # Highlight keywords (case insensitive)
    for keyword in SQL_KEYWORDS:
        pattern = r'\b(' + keyword + r')\b'
        query = re.sub(pattern, r"<span class='sql-keyword'>\1</span>", query, flags=re.IGNORECASE)
    
    # Highlight functions
    for func in SQL_FUNCTIONS:
        pattern = r'\b(' + func + r')\s*\('
        query = re.sub(pattern, r"<span class='sql-function'>\1</span>(", query, flags=re.IGNORECASE)
    
    return query


def get_query_type_badge(query_type: str) -> str:
    """
    Get CSS class for query type badge based on SQL concept.
    """
    query_type_lower = query_type.lower()
    
    if 'simple' in query_type_lower:
        return 'badge-simple'
    elif 'aggregate' in query_type_lower:
        return 'badge-aggregate'
    elif 'join' in query_type_lower:
        return 'badge-join'
    elif 'subquery' in query_type_lower and 'correlated' not in query_type_lower:
        return 'badge-subquery'
    elif 'correlated' in query_type_lower or '>= all' in query_type_lower or '> any' in query_type_lower:
        return 'badge-correlated'
    elif 'union' in query_type_lower:
        return 'badge-union'
    elif 'exists' in query_type_lower or 'not exists' in query_type_lower:
        return 'badge-subquery'
    else:
        return 'badge-simple'


def show_sql_console(
    query: str,
    title: str = "Current Query",
    query_type: str = "",
    execution_time: float = None,
    show: bool = True
) -> None:
    """
    Display the SQL query in a styled console panel.
    
    Args:
        query: SQL query string to display
        title: Title for the console panel
        query_type: Type of SQL concept being demonstrated
        execution_time: Time taken to execute the query in seconds
        show: Whether to show the console (can be controlled by session state)
    """
    if not show:
        return
    
    with st.expander(f"📟 SQL Console — {title}", expanded=True):
        # Query type badge and execution time in one row
        col1, col2 = st.columns([3, 1])
        with col1:
            if query_type:
                badge_class = get_query_type_badge(query_type)
                st.markdown(
                    f"<span class='query-badge {badge_class}'>{query_type}</span>",
                    unsafe_allow_html=True
                )
        with col2:
            if execution_time is not None:
                st.markdown(
                    f"<p style='text-align: right; font-size: 0.8rem; color: #94A3B8; margin: 0;'>⏱ Executed in {execution_time:.3f}s</p>",
                    unsafe_allow_html=True
                )
        
        # SQL Console with syntax highlighting
        st.code(query, language="sql")


def show_sql_console_minimal(
    query: str,
    query_type: str = "",
    key: str = None
) -> None:
    """
    Display SQL query in a minimal inline format.
    Useful for compact views.
    """
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            if query_type:
                badge_class = get_query_type_badge(query_type)
                st.markdown(
                    f"<span class='query-badge {badge_class}' style='font-size: 10px;'>{query_type}</span>",
                    unsafe_allow_html=True
                )
            st.code(query, language="sql")
        
        with col2:
            st.caption("SQL Query")


class SQLConsoleManager:
    """
    Manages SQL console state across pages.
    Stores query history and execution times.
    """
    
    def __init__(self):
        if 'sql_console_history' not in st.session_state:
            st.session_state.sql_console_history = []
        
        if 'sql_console_expanded' not in st.session_state:
            st.session_state.sql_console_expanded = True
    
    def add_query(
        self,
        query: str,
        title: str,
        query_type: str = "",
        execution_time: float = None,
        result_rows: int = None
    ) -> None:
        """
        Add a query to the console history.
        """
        entry = {
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'query': query,
            'title': title,
            'query_type': query_type,
            'execution_time': execution_time,
            'result_rows': result_rows
        }
        
        # Keep last 10 queries
        st.session_state.sql_console_history = (
            [entry] + st.session_state.sql_console_history
        )[:10]
    
    def get_history(self) -> list:
        """Get query history."""
        return st.session_state.sql_console_history
    
    def toggle_expanded(self) -> None:
        """Toggle console expanded state."""
        st.session_state.sql_console_expanded = not st.session_state.sql_console_expanded
    
    def clear_history(self) -> None:
        """Clear query history."""
        st.session_state.sql_console_history = []


def create_sql_console_manager() -> SQLConsoleManager:
    """Factory function to create SQL console manager."""
    return SQLConsoleManager()


def display_sql_console() -> None:
    """
    Display an interactive SQL console panel for exploring queries.
    This is a standalone console that allows users to view query history.
    """
    # Initialize session state
    if 'sql_console_history' not in st.session_state:
        st.session_state.sql_console_history = []

    st.markdown("### SQL Query Console")

    # Display history if any
    if st.session_state.sql_console_history:
        for entry in st.session_state.sql_console_history[:5]:  # Show last 5
            with st.expander(f"📟 {entry['title']} - {entry['timestamp']}", expanded=False):
                if entry.get('query_type'):
                    badge_class = get_query_type_badge(entry['query_type'])
                    st.markdown(
                        f"<span class='query-badge {badge_class}'>{entry['query_type']}</span>",
                        unsafe_allow_html=True
                    )
                if entry.get('execution_time') is not None:
                    st.caption(f"⏱ {entry['execution_time']:.3f}s")
                st.code(entry['query'], language="sql")
    else:
        st.info("SQL queries executed on this page will appear here.")


# Predefined query categories for SQL Explorer
QUERY_CATEGORIES = {
    "Simple Queries": [
        ("S1 - All Users", "simple_query"),
        ("S2 - All Exercises", "simple_query"),
        ("S3 - All Goals", "simple_query"),
        ("S4 - Recent Workouts", "simple_query"),
    ],
    "Aggregate Queries": [
        ("A1 - Users by Activity Level", "aggregate"),
        ("A2 - Users by Sex", "aggregate"),
        ("A3 - Avg Height by Sex", "aggregate"),
        ("A4 - Age Distribution", "aggregate"),
        ("A5 - Workouts per Day", "aggregate"),
        ("A6 - Most Popular Goals", "aggregate"),
        ("A7 - Conditions by Severity", "aggregate"),
        ("A8 - Avg Workout Duration", "aggregate"),
    ],
    "INNER JOIN Queries": [
        ("J1 - User Demographics", "inner_join"),
        ("J2 - Most Used Exercises", "inner_join"),
        ("J3 - Top Active Users", "inner_join"),
        ("J4 - Users with Severe Conditions", "inner_join"),
    ],
    "OUTER JOIN (LEFT JOIN)": [
        ("O1 - Users with No Goals", "outer_join"),
        ("O2 - Users with No Workouts", "outer_join"),
        ("O3 - Exercises Never Used", "outer_join"),
    ],
    "Nested Subqueries": [
        ("N1 - Users Above Avg Workouts", "nested_subquery"),
        ("N2 - Heaviest Lifts Above Avg", "nested_subquery"),
    ],
    "Correlated Subqueries": [
        ("C1 - Last Workout > Avg Duration", "correlated_subquery"),
        ("C2 - Users with More Goals Than Avg", "correlated_subquery"),
    ],
    "ALL / ANY / EXISTS": [
        ("E1 - User with Most Workouts (>= ALL)", "all_subquery"),
        ("E2 - Users Exceeding Sleep Target (> ANY)", "any_subquery"),
        ("E3 - Users Who Logged Weight (EXISTS)", "exists"),
        ("E4 - Users Who Never Logged Sleep (NOT EXISTS)", "not_exists"),
    ],
    "UNION / UNION ALL": [
        ("U1 - Table Row Counts", "union"),
        ("U2 - Users with Goals OR Conditions", "union"),
        ("U3 - Combined Tracking Data", "union"),
    ],
    "Subqueries in SELECT/FROM": [
        ("SS1 - User Summary", "subquery_select"),
        ("SF1 - Avg Workouts Per User", "subquery_from"),
        ("SF2 - Activity Level with %", "subquery_from"),
    ],
}
