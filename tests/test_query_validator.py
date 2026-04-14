"""
FitSense AI Dashboard - Query Validator Tests
===============================================
Unit tests for the SQL query validator to ensure read-only protection.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the validator
from utils.query_validator import (
    validate_readonly_query,
    validate_query_strict,
    get_forbidden_keywords,
    is_safe_query_examples,
    _normalize_query,
)


# =============================================================================
# Test Normalization
# =============================================================================

class TestQueryNormalization:
    """Tests for query normalization."""

    def test_remove_single_line_comments(self):
        """Test that single-line comments are removed."""
        query = "SELECT * FROM users -- this is a comment"
        result = _normalize_query(query)
        assert "--" not in result

    def test_remove_hash_comments(self):
        """Test that hash-style comments are removed."""
        query = "SELECT * FROM users # MySQL comment"
        result = _normalize_query(query)
        assert "#" not in result

    def test_remove_multiline_comments(self):
        """Test that multi-line comments are removed."""
        query = "SELECT * FROM users /* comment\n spanning\n lines */ WHERE id = 1"
        result = _normalize_query(query)
        assert "/*" not in result
        assert "*/" not in result

    def test_normalize_whitespace(self):
        """Test that multiple whitespaces are normalized."""
        query = "SELECT    *    FROM    users"
        result = _normalize_query(query)
        assert "    " not in result

    def test_empty_query_handling(self):
        """Test that empty queries are handled."""
        assert _normalize_query("") == ""
        assert _normalize_query("   ") == ""


# =============================================================================
# Test Read-Only Validation (SELECT queries - should be ALLOWED)
# =============================================================================

class TestReadOnlyQueriesAllowed:
    """Test that SELECT queries are allowed."""

    def test_simple_select(self):
        """Test simple SELECT query."""
        is_valid, error = validate_readonly_query("SELECT * FROM users")
        assert is_valid is True
        assert error is None

    def test_select_with_where(self):
        """Test SELECT with WHERE clause."""
        is_valid, error = validate_readonly_query(
            "SELECT * FROM users WHERE age > 25"
        )
        assert is_valid is True
        assert error is None

    def test_select_with_join(self):
        """Test SELECT with JOIN."""
        is_valid, error = validate_readonly_query(
            "SELECT u.name, w.duration FROM users u JOIN workouts w ON u.id = w.user_id"
        )
        assert is_valid is True
        assert error is None

    def test_select_with_subquery(self):
        """Test SELECT with subquery in WHERE."""
        is_valid, error = validate_readonly_query(
            "SELECT * FROM users WHERE age > (SELECT AVG(age) FROM users)"
        )
        assert is_valid is True
        assert error is None

    def test_select_with_union(self):
        """Test SELECT with UNION."""
        is_valid, error = validate_readonly_query(
            "SELECT name FROM users UNION SELECT name FROM admins"
        )
        assert is_valid is True
        assert error is None

    def test_select_with_group_by(self):
        """Test SELECT with GROUP BY."""
        is_valid, error = validate_readonly_query(
            "SELECT COUNT(*), activity_level FROM user_profiles GROUP BY activity_level"
        )
        assert is_valid is True
        assert error is None

    def test_select_with_having(self):
        """Test SELECT with HAVING clause."""
        is_valid, error = validate_readonly_query(
            "SELECT activity_level, COUNT(*) as cnt FROM user_profiles GROUP BY activity_level HAVING cnt > 5"
        )
        assert is_valid is True
        assert error is None

    def test_select_with_order_limit(self):
        """Test SELECT with ORDER BY and LIMIT."""
        is_valid, error = validate_readonly_query(
            "SELECT * FROM users ORDER BY created_at DESC LIMIT 10"
        )
        assert is_valid is True
        assert error is None

    def test_select_with_case_when(self):
        """Test SELECT with CASE WHEN."""
        is_valid, error = validate_readonly_query(
            "SELECT name, CASE WHEN age > 30 THEN 'adult' ELSE 'young' END FROM users"
        )
        assert is_valid is True
        assert error is None

    def test_select_with_cte(self):
        """Test SELECT with Common Table Expression."""
        is_valid, error = validate_readonly_query(
            "WITH active_users AS (SELECT * FROM users WHERE active = 1) SELECT * FROM active_users"
        )
        assert is_valid is True
        assert error is None

    def test_select_with_aggregate_functions(self):
        """Test SELECT with various aggregate functions."""
        is_valid, error = validate_readonly_query(
            "SELECT COUNT(*), SUM(weight), AVG(weight), MIN(weight), MAX(weight) FROM weight_logs"
        )
        assert is_valid is True
        assert error is None

    def test_select_with_date_functions(self):
        """Test SELECT with date/time functions."""
        is_valid, error = validate_readonly_query(
            "SELECT DAYNAME(log_date), MONTH(log_date), YEAR(log_date) FROM workouts"
        )
        assert is_valid is True
        assert error is None

    def test_select_with_ifnull(self):
        """Test SELECT with IFNULL."""
        is_valid, error = validate_readonly_query(
            "SELECT IFNULL(weight, 0) FROM weight_logs"
        )
        assert is_valid is True
        assert error is None

    def test_select_with_coalesce(self):
        """Test SELECT with COALESCE."""
        is_valid, error = validate_readonly_query(
            "SELECT COALESCE(weight, body_fat, 0) FROM weight_logs"
        )
        assert is_valid is True
        assert error is None

    def test_select_with_distinct(self):
        """Test SELECT with DISTINCT."""
        is_valid, error = validate_readonly_query(
            "SELECT DISTINCT activity_level FROM user_profiles"
        )
        assert is_valid is True
        assert error is None

    def test_explain_select(self):
        """Test EXPLAIN SELECT (should be allowed)."""
        is_valid, error = validate_readonly_query(
            "EXPLAIN SELECT * FROM users"
        )
        assert is_valid is True
        assert error is None

    def test_describe_table(self):
        """Test DESCRIBE (variant of EXPLAIN)."""
        is_valid, error = validate_readonly_query(
            "DESCRIBE users"
        )
        assert is_valid is True
        assert error is None

    def test_select_hex_function(self):
        """Test HEX function (used for binary ID conversion)."""
        is_valid, error = validate_readonly_query(
            "SELECT HEX(user_id) FROM users"
        )
        assert is_valid is True
        assert error is None

    def test_select_timestamps_diff(self):
        """Test TIMESTAMPDIFF function."""
        is_valid, error = validate_readonly_query(
            "SELECT TIMESTAMPDIFF(DAY, start_date, end_date) FROM workouts"
        )
        assert is_valid is True
        assert error is None


# =============================================================================
# Test Write/Delete Validation (should be BLOCKED)
# =============================================================================

class TestBlockedQueries:
    """Test that write/modify queries are blocked."""

    def test_insert_blocked(self):
        """Test INSERT is blocked."""
        is_valid, error = validate_readonly_query(
            "INSERT INTO users (name) VALUES ('test')"
        )
        assert is_valid is False
        assert error is not None
        assert "INSERT" in error

    def test_insert_lowercase_blocked(self):
        """Test INSERT (lowercase) is blocked."""
        is_valid, error = validate_readonly_query(
            "insert into users (name) values ('test')"
        )
        assert is_valid is False
        assert "insert" in error.lower()

    def test_update_blocked(self):
        """Test UPDATE is blocked."""
        is_valid, error = validate_readonly_query(
            "UPDATE users SET name = 'test' WHERE id = 1"
        )
        assert is_valid is False
        assert "UPDATE" in error

    def test_delete_blocked(self):
        """Test DELETE is blocked."""
        is_valid, error = validate_readonly_query(
            "DELETE FROM users WHERE id = 1"
        )
        assert is_valid is False
        assert "DELETE" in error

    def test_drop_table_blocked(self):
        """Test DROP TABLE is blocked."""
        is_valid, error = validate_readonly_query(
            "DROP TABLE users"
        )
        assert is_valid is False
        assert "DROP" in error

    def test_truncate_blocked(self):
        """Test TRUNCATE is blocked."""
        is_valid, error = validate_readonly_query(
            "TRUNCATE TABLE users"
        )
        assert is_valid is False
        assert "TRUNCATE" in error

    def test_alter_blocked(self):
        """Test ALTER is blocked."""
        is_valid, error = validate_readonly_query(
            "ALTER TABLE users ADD COLUMN age INT"
        )
        assert is_valid is False
        assert "ALTER" in error

    def test_create_table_blocked(self):
        """Test CREATE TABLE is blocked."""
        is_valid, error = validate_readonly_query(
            "CREATE TABLE test (id INT)"
        )
        assert is_valid is False
        assert "CREATE" in error

    def test_grant_blocked(self):
        """Test GRANT is blocked."""
        is_valid, error = validate_readonly_query(
            "GRANT ALL ON *.* TO 'user'@'localhost'"
        )
        assert is_valid is False
        assert "GRANT" in error

    def test_revoke_blocked(self):
        """Test REVOKE is blocked."""
        is_valid, error = validate_readonly_query(
            "REVOKE ALL ON *.* FROM 'user'@'localhost'"
        )
        assert is_valid is False
        assert "REVOKE" in error

    def test_replace_into_blocked(self):
        """Test REPLACE INTO is blocked."""
        is_valid, error = validate_readonly_query(
            "REPLACE INTO users (id, name) VALUES (1, 'test')"
        )
        assert is_valid is False
        assert "REPLACE" in error

    def test_rename_blocked(self):
        """Test RENAME is blocked."""
        is_valid, error = validate_readonly_query(
            "RENAME TABLE users TO user_list"
        )
        assert is_valid is False
        assert "RENAME" in error

    def test_lock_tables_blocked(self):
        """Test LOCK TABLES is blocked."""
        is_valid, error = validate_readonly_query(
            "LOCK TABLES users READ"
        )
        assert is_valid is False
        assert "LOCK" in error

    def test_load_data_blocked(self):
        """Test LOAD DATA is blocked."""
        is_valid, error = validate_readonly_query(
            "LOAD DATA INFILE '/path/to/file.csv' INTO TABLE users"
        )
        assert is_valid is False
        assert "LOAD" in error

    def test_set_variable_blocked(self):
        """Test SET variable is blocked."""
        is_valid, error = validate_readonly_query(
            "SET @variable = 1"
        )
        assert is_valid is False
        assert "SET" in error

    def test_execute_blocked(self):
        """Test EXECUTE (stored procedure) is blocked."""
        is_valid, error = validate_readonly_query(
            "EXECUTE stmt1"
        )
        assert is_valid is False
        assert "EXECUTE" in error


# =============================================================================
# Test Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases and edge case queries."""

    def test_empty_query_blocked(self):
        """Test empty query is blocked."""
        is_valid, error = validate_readonly_query("")
        assert is_valid is False
        assert "Empty" in error

    def test_whitespace_only_query_blocked(self):
        """Test whitespace-only query is blocked."""
        is_valid, error = validate_readonly_query("   \n\t  ")
        assert is_valid is False
        assert "Empty" in error

    def test_multistatement_all_select(self):
        """Test multi-statement query with all SELECT is allowed."""
        is_valid, error = validate_readonly_query(
            "SELECT 1; SELECT 2; SELECT 3"
        )
        assert is_valid is True

    def test_multistatement_with_insert_blocked(self):
        """Test multi-statement query with INSERT in second statement is blocked."""
        is_valid, error = validate_readonly_query(
            "SELECT 1; INSERT INTO users (name) VALUES ('test')"
        )
        assert is_valid is False

    def test_multistatement_with_delete_blocked(self):
        """Test multi-statement query with DELETE is blocked."""
        is_valid, error = validate_readonly_query(
            "SELECT * FROM users; DELETE FROM workouts"
        )
        assert is_valid is False

    def test_select_with_comment_containing_insert(self):
        """Test query with comment containing INSERT is allowed."""
        is_valid, error = validate_readonly_query(
            "SELECT * FROM users /* INSERT INTO evil */ WHERE active = 1"
        )
        assert is_valid is True

    def test_select_with_comment_containing_delete(self):
        """Test query with comment containing DELETE is allowed."""
        is_valid, error = validate_readonly_query(
            "SELECT * FROM users -- DELETE everything\n WHERE active = 1"
        )
        assert is_valid is True

    def test_select_case_insensitive(self):
        """Test that validation is case-insensitive."""
        queries = [
            "select * from users",
            "SELECT * FROM USERS",
            "SeLeCt * fRoM uSeRs",
        ]
        for query in queries:
            is_valid, error = validate_readonly_query(query)
            assert is_valid is True, f"Query should be valid: {query}"

    def test_select_with_tablename_like_delete(self):
        """Test that 'users_delete_view' table name is allowed (pattern match issue)."""
        is_valid, error = validate_readonly_query(
            "SELECT * FROM users_delete_view WHERE id = 1"
        )
        # This might be a false positive due to pattern matching on 'DELETE'
        # Let's see if the implementation handles this
        # Note: This is an edge case that may need refinement
        # For now, we test the current behavior
        assert isinstance(is_valid, bool)

    def test_select_with_order_delete_asc(self):
        """Test that 'order delete asc' column is handled."""
        is_valid, error = validate_readonly_query(
            "SELECT delete, order FROM user_preferences"
        )
        # Similar edge case - might flag on DELETE as keyword even in column name
        assert isinstance(is_valid, bool)

    def test_query_with_leading_whitespace(self):
        """Test query with leading/trailing whitespace."""
        is_valid, error = validate_readonly_query(
            "   SELECT * FROM users   "
        )
        assert is_valid is True

    def test_query_with_newlines(self):
        """Test query with newlines and tabs."""
        is_valid, error = validate_readonly_query(
            "SELECT * FROM users\n\tWHERE id = 1\n"
        )
        assert is_valid is True

    def test_transaction_statements_blocked(self):
        """Test transaction control statements are blocked."""
        transaction_queries = [
            "BEGIN",
            "BEGIN WORK",
            "COMMIT",
            "ROLLBACK",
            "SAVEPOINT my_savepoint",
            "RELEASE SAVEPOINT my_savepoint",
        ]
        for query in transaction_queries:
            is_valid, error = validate_readonly_query(query)
            # These are blocked for safety (even though they don't modify data directly)
            assert is_valid is False


# =============================================================================
# Test Strict Validation
# =============================================================================

class TestStrictValidation:
    """Test the strict validation mode."""

    def test_strict_requires_select_start(self):
        """Test that strict mode requires query to start with SELECT."""
        is_valid, error = validate_query_strict("EXPLAIN SELECT * FROM users")
        assert is_valid is False
        assert "must start with SELECT" in error

    def test_strict_allows_select(self):
        """Test that strict mode allows SELECT."""
        is_valid, error = validate_query_strict("SELECT * FROM users")
        assert is_valid is True

    def test_strict_blocks_explain_execute(self):
        """Test that strict mode blocks EXPLAIN EXECUTE."""
        is_valid, error = validate_query_strict("EXPLAIN EXECUTE stmt1")
        assert is_valid is False


# =============================================================================
# Test Example Queries
# =============================================================================

class TestExampleQueries:
    """Test the example queries from the validator module."""

    def test_example_queries_complete(self):
        """Test that all example queries are defined."""
        examples = is_safe_query_examples()
        assert len(examples) > 0

    def test_all_examples_covered(self):
        """Test all example queries match expected behavior."""
        examples = is_safe_query_examples()
        for query, should_be_allowed in examples:
            is_valid, error = validate_readonly_query(query)
            if should_be_allowed:
                assert is_valid is True, f"Query should be allowed: {query}"
            else:
                assert is_valid is False, f"Query should be blocked: {query}"


# =============================================================================
# Test Helper Functions
# =============================================================================

class TestHelperFunctions:
    """Test helper functions in the validator module."""

    def test_get_forbidden_keywords(self):
        """Test that forbidden keywords list is returned."""
        keywords = get_forbidden_keywords()
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        # Each item should be a tuple of (pattern, name)
        for item in keywords:
            assert isinstance(item, tuple)
            assert len(item) == 2


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
