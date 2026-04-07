"""
SQL Query Validator for FitSense AI Dashboard
Ensures all queries are read-only (SELECT only) for security.
"""

import re
from typing import Tuple, List, Optional


# Forbidden SQL keywords and patterns that indicate data modification
# These are case-insensitive patterns that should block execution
FORBIDDEN_PATTERNS = [
    # Data modification keywords
    (r'\bINSERT\s+INTO\b', 'INSERT INTO'),
    (r'\bREPLACE\s+INTO\b', 'REPLACE INTO'),
    (r'\bUPDATE\b', 'UPDATE'),
    (r'\bDELETE\s+FROM\b', 'DELETE FROM'),
    (r'\bTRUNCATE\b', 'TRUNCATE'),

    # DDL (Data Definition Language) - schema modifications
    (r'\bCREATE\b', 'CREATE'),
    (r'\bDROP\b', 'DROP'),
    (r'\bALTER\b', 'ALTER'),
    (r'\bRENAME\b', 'RENAME'),
    (r'\bMODIFY\b', 'MODIFY'),
    (r'\bCHANGE\b', 'CHANGE'),

    # DCL (Data Control Language) - permissions
    (r'\bGRANT\b', 'GRANT'),
    (r'\bREVOKE\b', 'REVOKE'),

    # Administrative commands
    (r'\bSHUTDOWN\b', 'SHUTDOWN'),
    (r'\bKILL\b', 'KILL'),
    (r'\bFLUSH\b', 'FLUSH'),
    (r'\bRESET\b', 'RESET'),
    (r'\bSET\b(?!\s+HIGH)', 'SET'),  # SET without HIGH (MySQL specific)
    (r'\bLOAD\b', 'LOAD'),
    (r'\bLOCK\b', 'LOCK'),
    (r'\bUNLOCK\b', 'UNLOCK'),

    # Stored procedures and functions
    (r'\bCALL\b', 'CALL'),
    (r'\bEXECUTE\b', 'EXECUTE'),
    (r'\bEXPLAIN\s+EXECUTE\b', 'EXPLAIN EXECUTE'),  # Only block EXPLAIN EXECUTE (procedures), not EXPLAIN SELECT

    # Transaction control (these don't modify data but we want to block them for safety)
    (r'\bBEGIN\b', 'BEGIN'),
    (r'\bCOMMIT\b', 'COMMIT'),
    (r'\bROLLBACK\b', 'ROLLBACK'),
    (r'\bSAVEPOINT\b', 'SAVEPOINT'),
    (r'\bRELEASE\s+SAVEPOINT\b', 'RELEASE SAVEPOINT'),

    # XA transactions
    (r'\bXA\s+BEGIN\b', 'XA BEGIN'),
    (r'\bXA\s+COMMIT\b', 'XA COMMIT'),
    (r'\bXA\s+ROLLBACK\b', 'XA ROLLBACK'),
]

# Allowed SQL keywords that are commonly used in SELECT queries
# These should NOT trigger a block
ALLOWED_KEYWORDS = [
    'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'IN', 'EXISTS', 'BETWEEN',
    'LIKE', 'IS', 'NULL', 'AS', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'OUTER',
    'FULL', 'CROSS', 'ON', 'USING', 'GROUP', 'BY', 'HAVING', 'ORDER',
    'ASC', 'DESC', 'LIMIT', 'OFFSET', 'UNION', 'ALL', 'INTERSECT', 'EXCEPT',
    'WITH', 'RECURSIVE',  # CTE support
    'DISTINCT', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'CASE', 'WHEN',
    'THEN', 'ELSE', 'END', 'CAST', 'CONVERT', 'COALESCE', 'IFNULL',
    'TIMESTAMPDIFF', 'YEAR', 'MONTH', 'DAY', 'HOUR', 'MINUTE', 'SECOND',
    'DATE', 'NOW', 'CURDATE', 'DAYOFWEEK', 'DAYNAME', 'ROUND', 'FLOOR', 'CEIL',
    'HEX', 'BIN', 'CONCAT', 'SUBSTRING', 'LENGTH', 'UPPER', 'LOWER', 'TRIM',
    'ABS', 'MOD', 'POWER', 'SQRT', 'IF', 'NULLIF',
    'VARIANCE', 'STDDEV', 'STD', 'GROUP_CONCAT',
]

# Keywords that need careful handling (may appear in SELECT but also in DML)
AMBIGUOUS_KEYWORDS = [
    ('SET', 'Setting variables (blocked for safety)'),
    ('DO', 'DO statement (blocked for safety)'),
    ('HANDLER', 'HANDLER statement (blocked for safety)'),
]


def validate_readonly_query(query: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that a SQL query is read-only (does not modify data or schema).

    Args:
        query: SQL query string to validate

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if the query is read-only, False otherwise
        - error_message: Description of the violation if not valid, None if valid
    """
    if not query or not query.strip():
        return False, "Empty query provided"

    # Normalize the query: remove comments, extra whitespace
    normalized_query = _normalize_query(query)

    # Check each forbidden pattern
    for pattern, keyword_name in FORBIDDEN_PATTERNS:
        match = re.search(pattern, normalized_query, re.IGNORECASE)
        if match:
            # Provide a helpful error message
            return False, f"Forbidden operation detected: '{match.group(0).strip()}'. This dashboard only allows SELECT queries for read-only access."

    # Additional safety checks
    # Check for multiple statements (semicolon-separated) - all must be valid
    statements = normalized_query.split(';')
    for i, stmt in enumerate(statements):
        stmt = stmt.strip()
        if stmt and stmt.upper() not in ('BEGIN', 'END'):
            # Check for forbidden patterns in each statement
            for pattern, keyword_name in FORBIDDEN_PATTERNS:
                if re.search(pattern, stmt, re.IGNORECASE):
                    return False, f"Forbidden operation in statement {i+1}: '{keyword_name}'. This dashboard only allows SELECT queries."

    # Check for EXPLAIN EXECUTE (procedures)
    if re.search(r'\bEXPLAIN\s+EXECUTE\b', normalized_query, re.IGNORECASE):
        return False, "EXECUTE statement blocked. This dashboard only allows SELECT queries."

    # If all checks pass, the query is read-only
    return True, None


def _normalize_query(query: str) -> str:
    """
    Normalize a SQL query for validation.
    Removes comments, extra whitespace, and normalizes case.
    """
    # Remove single-line comments (-- style)
    query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)

    # Remove single-line comments (# style - MySQL)
    query = re.sub(r'#.*$', '', query, flags=re.MULTILINE)

    # Remove multi-line comments (/* */ style)
    query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)

    # Normalize whitespace
    query = re.sub(r'\s+', ' ', query)

    # Normalize case for checking (but preserve for display)
    return query.strip()


def validate_query_strict(query: str) -> Tuple[bool, Optional[str]]:
    """
    Strict validation that only allows pure SELECT statements.
    This is more restrictive than validate_readonly_query().

    Use this for maximum security where only basic SELECT is needed.
    """
    if not query or not query.strip():
        return False, "Empty query provided"

    normalized = _normalize_query(query).upper()
    normalized_no_comments = _normalize_query(query)

    # Check that query starts with SELECT
    if not normalized.startswith('SELECT'):
        return False, "Query must start with SELECT. This dashboard only allows SELECT queries."

    # Block any forbidden patterns even within complex SELECT
    for pattern, keyword_name in FORBIDDEN_PATTERNS:
        if re.search(pattern, normalized_no_comments, re.IGNORECASE):
            return False, f"Forbidden operation detected: '{keyword_name}'. This dashboard only allows SELECT queries."

    # Block subqueries that contain modifications (double check)
    if re.search(r'\bINSERT\b', normalized, re.IGNORECASE):
        return False, "INSERT statement detected. This dashboard only allows SELECT queries."

    if re.search(r'\bUPDATE\b', normalized, re.IGNORECASE):
        return False, "UPDATE statement detected. This dashboard only allows SELECT queries."

    if re.search(r'\bDELETE\b', normalized, re.IGNORECASE):
        return False, "DELETE statement detected. This dashboard only allows SELECT queries."

    return True, None


def get_forbidden_keywords() -> List[Tuple[str, str]]:
    """
    Return the list of forbidden keywords for documentation/reference.
    """
    return FORBIDDEN_PATTERNS.copy()


def is_safe_query_examples() -> List[Tuple[str, bool]]:
    """
    Return example queries for testing the validator.
    Returns list of (query_example, should_be_allowed) tuples.
    """
    return [
        # Should be allowed (SELECT queries)
        ("SELECT * FROM users", True),
        ("SELECT COUNT(*) FROM workouts", True),
        ("SELECT u.name, w.duration FROM users u JOIN workouts w ON u.id = w.user_id", True),
        ("SELECT * FROM users WHERE age > (SELECT AVG(age) FROM users)", True),
        ("SELECT name FROM users UNION SELECT name FROM admins", True),
        ("WITH cte AS (SELECT id FROM users) SELECT * FROM cte", True),
        ("SELECT IFNULL(weight, 0) FROM weight_logs", True),
        ("SELECT CASE WHEN score > 50 THEN 'pass' ELSE 'fail' END FROM tests", True),

        # Should be blocked (write/delete operations)
        ("INSERT INTO users (name) VALUES ('test')", False),
        ("UPDATE users SET name = 'test' WHERE id = 1", False),
        ("DELETE FROM users WHERE id = 1", False),
        ("DROP TABLE users", False),
        ("TRUNCATE TABLE users", False),
        ("CREATE TABLE test (id INT)", False),
        ("ALTER TABLE users ADD COLUMN age INT", False),
        ("GRANT ALL ON *.* TO 'user'@'localhost'", False),
        ("SELECT * FROM users; DROP TABLE users", False),  # Multi-statement with danger
        ("SELECT * FROM users; DELETE FROM workouts", False),
    ]
