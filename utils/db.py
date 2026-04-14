"""
Database Connection Utility for FitSense AI Dashboard
Handles MySQL connection with connection pooling and retry logic.

SECURITY NOTE: This dashboard is configured for READ-ONLY access.
All queries are validated to ensure only SELECT statements are executed.
Write operations (INSERT, UPDATE, DELETE, DROP, etc.) are blocked at the
application level for data protection.
"""

import os
import time
import pandas as pd
from contextlib import contextmanager
from typing import Optional, Dict, Any, Generator
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error, pooling

# Import query validator for read-only enforcement
from utils.query_validator import validate_readonly_query

# Load environment variables - prioritize .env.local over .env
load_dotenv()  # Load default .env first
load_dotenv('.env.local', override=True)  # Override with .env.local

# Failsafe: Set to True only if write operations are explicitly needed
# WARNING: Setting to True allows data modification - use with extreme caution
ALLOW_WRITE_QUERIES = False

# Connection pool configuration
_connection_pool: Optional[pooling.MySQLConnectionPool] = None
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds


def get_connection_config() -> Dict[str, Any]:
    """Get database connection configuration from environment variables."""
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'fitsense_ai'),
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci',
        'autocommit': False,  # Disabled for read-only safety
        'consume_results': True,  # Consume all results to prevent "unread result" errors
    }


def init_connection_pool() -> pooling.MySQLConnectionPool:
    """Initialize the MySQL connection pool."""
    global _connection_pool
    
    config = get_connection_config()
    
    pool_config = {
        'pool_name': 'fitsense_pool',
        'pool_size': 5,
        'pool_reset_session': True,
        'host': config['host'],
        'port': config['port'],
        'user': config['user'],
        'password': config['password'],
        'database': config['database'],
        'charset': config['charset'],
        'collation': config['collation'],
    }
    
    _connection_pool = pooling.MySQLConnectionPool(**pool_config)
    return _connection_pool


def get_connection_pool() -> pooling.MySQLConnectionPool:
    """Get or create the connection pool."""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = init_connection_pool()
    return _connection_pool


@contextmanager
def get_connection() -> Generator:
    """
    Context manager for database connections with retry logic.
    Usage:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
    """
    pool = get_connection_pool()
    retries = 0
    conn = None

    while retries < MAX_RETRIES:
        try:
            conn = pool.get_connection()
            break
        except Error as e:
            retries += 1
            if retries >= MAX_RETRIES:
                raise ConnectionError(f"Failed to connect after {MAX_RETRIES} retries: {e}")
            time.sleep(RETRY_DELAY * retries)  # Exponential backoff

    try:
        yield conn
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


def execute_query(query: str, params: tuple = None) -> pd.DataFrame:
    """
    Execute a SELECT query and return results as a DataFrame.

    SECURITY: This function enforces read-only access by validating that
    the query is a SELECT statement before execution.

    Args:
        query: SQL SELECT query
        params: Optional tuple of parameters for prepared statements

    Returns:
        DataFrame with query results

    Raises:
        ValueError: If the query is not a read-only SELECT statement
    """
    # Validate that the query is read-only (SELECT only)
    is_valid, error_message = validate_readonly_query(query)
    if not is_valid:
        raise ValueError(f"Read-only violation: {error_message}")

    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        results = cursor.fetchall()
        df = pd.DataFrame(results)

        # Convert binary UUID columns to hex strings for better readability
        # Binary columns typically have names ending with '_id'
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    # Check if it's a binary column (contains bytes)
                    non_null_values = df[col].dropna()
                    if len(non_null_values) > 0:
                        sample = non_null_values.iloc[0]
                        if sample is not None and isinstance(sample, (bytes, bytearray)):
                            df[col] = df[col].apply(
                                lambda x: x.hex() if isinstance(x, (bytes, bytearray)) else x
                            )
                except (IndexError, AttributeError, TypeError):
                    pass

        return df


def execute_write_query(query: str, params: tuple = None) -> int:
    """
    Execute an INSERT, UPDATE, or DELETE query.

    SECURITY: This function is DISABLED by default for read-only safety.
    The dashboard is configured to only allow SELECT queries.

    Args:
        query: SQL write query
        params: Optional tuple of parameters

    Returns:
        Number of affected rows

    Raises:
        PermissionError: Always raised - write operations are blocked
    """
    raise PermissionError(
        "Write operations are disabled. This dashboard only supports read-only "
        "(SELECT) queries for data protection. To enable write operations, "
        "you must explicitly set ALLOW_WRITE_QUERIES = True in utils/db.py "
        "and understand the security implications."
    )


def test_connection() -> bool:
    """
    Test database connection and return status.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False


def ensure_db_connection():
    """
    Ensure database connection is established for the current session.
    This function should be called at the beginning of any page that needs database access.
    It initializes session state and tests the connection silently.
    
    Note: Requires Streamlit (import streamlit as st) in the calling module.
    """
    import streamlit as st
    
    # Initialize session state if not present
    if "db_connected" not in st.session_state:
        st.session_state.db_connected = False
    
    # Test connection if not already connected
    if not st.session_state.db_connected:
        connected = test_connection()
        st.session_state.db_connected = connected


def get_table_row_counts() -> Dict[str, int]:
    """
    Get row counts for all tables in the database.
    
    Returns:
        Dictionary mapping table names to row counts
    """
    query = """
        SELECT TABLE_NAME, TABLE_ROWS 
        FROM information_schema.tables 
        WHERE TABLE_SCHEMA = %s
        AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """
    
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (get_connection_config()['database'],))
        results = cursor.fetchall()
        return {row['TABLE_NAME']: row['TABLE_ROWS'] for row in results}


# Initialize pool on module import
try:
    init_connection_pool()
except Exception as e:
    print(f"Warning: Could not initialize connection pool: {e}")
