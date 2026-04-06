"""
FitSense AI Dashboard - Test Suite
===================================
Unit and integration tests for the dashboard.
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# =============================================================================
# Test Configuration
# =============================================================================

@pytest.fixture
def mock_env():
    """Mock environment variables for testing."""
    env_vars = {
        'DB_HOST': 'localhost',
        'DB_PORT': '3306',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_NAME': 'test_db',
        'DEMO_MODE': 'true'
    }
    with patch.dict(os.environ, env_vars, clear=True):
        yield env_vars


@pytest.fixture
def sample_dataframe():
    """Create sample dataframe for testing."""
    return pd.DataFrame({
        'user_id': [1, 2, 3, 4, 5],
        'username': ['user1', 'user2', 'user3', 'user4', 'user5'],
        'age': [25, 30, 35, 40, 45],
        'activity_level': ['sedentary', 'lightly_active', 'moderately_active', 'very_active', 'sedentary']
    })


# =============================================================================
# Database Tests
# =============================================================================

class TestDatabaseConnection:
    """Tests for database connection module."""
    
    def test_connection_config_from_env(self, mock_env):
        """Test that connection config is read from environment."""
        # This will use mock environment
        assert os.getenv('DB_HOST') == 'localhost'
        assert os.getenv('DB_PORT') == '3306'
    
    def test_connection_string_format(self, mock_env):
        """Test connection string formatting."""
        host = os.getenv('DB_HOST')
        port = os.getenv('DB_PORT')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        db = os.getenv('DB_NAME')
        
        conn_string = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}"
        assert 'mysql+mysqlconnector://' in conn_string
        assert '@localhost:3306/' in conn_string


# =============================================================================
# Chart Tests
# =============================================================================

class TestChartGeneration:
    """Tests for chart generation utilities."""
    
    def test_template_config_exists(self):
        """Test that chart template configuration exists."""
        from utils.charts import CHART_TEMPLATE
        
        assert 'layout' in CHART_TEMPLATE
        assert 'paper_bgcolor' in CHART_TEMPLATE['layout']
    
    def test_color_palette_not_empty(self):
        """Test that color palette is defined."""
        from utils.charts import CHART_COLORS
        
        assert len(CHART_COLORS) > 0
        assert '#3B82F6' in CHART_COLORS  # Primary blue
    
    def test_scatter_chart_creation(self, sample_dataframe):
        """Test scatter chart generation."""
        from utils.charts import create_scatter_chart
        
        fig = create_scatter_chart(
            sample_dataframe,
            x='age',
            y='user_id',
            title='Test Scatter'
        )
        
        assert fig is not None
        assert len(fig.data) == 1
    
    def test_bar_chart_creation(self, sample_dataframe):
        """Test bar chart generation."""
        from utils.charts import create_bar_chart
        
        # Create aggregated data for bar chart
        agg_df = sample_dataframe.groupby('activity_level')['age'].mean().reset_index()
        
        fig = create_bar_chart(
            agg_df,
            x='activity_level',
            y='age',
            title='Test Bar'
        )
        
        assert fig is not None


# =============================================================================
# Query Tests
# =============================================================================

class TestQueryDefinitions:
    """Tests for SQL query definitions."""
    
    def test_simple_queries_exist(self):
        """Test that simple queries are defined."""
        from utils.queries import S1_ALL_USERS, S2_ALL_EXERCISES
        
        assert isinstance(S1_ALL_USERS, str)
        assert "SELECT" in S1_ALL_USERS.upper()
    
    def test_aggregate_queries_exist(self):
        """Test that aggregate queries are defined."""
        from utils.queries import A1_USERS_BY_ACTIVITY_LEVEL, A2_USERS_BY_SEX
        
        assert isinstance(A1_USERS_BY_ACTIVITY_LEVEL, str)
        assert "GROUP BY" in A1_USERS_BY_ACTIVITY_LEVEL.upper()
    
    def test_join_queries_exist(self):
        """Test that JOIN queries are defined."""
        from utils.queries import J1_USER_PROFILES_DEMOGRAPHICS
        
        assert isinstance(J1_USER_PROFILES_DEMOGRAPHICS, str)
        assert "JOIN" in J1_USER_PROFILES_DEMOGRAPHICS.upper()
    
    def test_subquery_queries_exist(self):
        """Test that subquery queries are defined."""
        from utils.queries import N1_USERS_ABOVE_AVERAGE_WORKOUTS
        
        assert isinstance(N1_USERS_ABOVE_AVERAGE_WORKOUTS, str)
        assert "SELECT" in N1_USERS_ABOVE_AVERAGE_WORKOUTS.upper()
    
    def test_query_metadata_exists(self):
        """Test that query metadata is defined."""
        from utils.queries import QUERY_METADATA
        
        assert isinstance(QUERY_METADATA, dict)
        assert 'A1' in QUERY_METADATA
        assert 'J1' in QUERY_METADATA
        assert 'N1' in QUERY_METADATA


# =============================================================================
# Cache Tests
# =============================================================================

class TestCache:
    """Tests for caching utilities."""
    
    def test_cache_initialization(self):
        """Test cache initialization."""
        from utils.cache import QueryCache
        
        cache = QueryCache(default_ttl=300)
        assert cache.default_ttl == 300
        assert len(cache._cache) == 0
    
    def test_cache_set_and_get(self, sample_dataframe):
        """Test cache set and get operations."""
        from utils.cache import QueryCache
        
        cache = QueryCache()
        cache.set("test_key", sample_dataframe)
        
        result = cache.get("test_key")
        assert result is not None
        assert len(result) == len(sample_dataframe)
    
    def test_cache_invalidation(self, sample_dataframe):
        """Test cache invalidation."""
        from utils.cache import QueryCache
        
        cache = QueryCache()
        cache.set("test_key", sample_dataframe)
        
        cache.invalidate()
        assert len(cache._cache) == 0


# =============================================================================
# Error Handler Tests
# =============================================================================

class TestErrorHandling:
    """Tests for error handling utilities."""
    
    def test_dashboard_error_creation(self):
        """Test DashboardError creation."""
        from utils.error_handler import DashboardError
        
        error = DashboardError("Test error", error_code="TEST", details={"key": "value"})
        assert error.message == "Test error"
        assert error.error_code == "TEST"
        assert error.details["key"] == "value"
    
    def test_database_error_creation(self):
        """Test DatabaseError creation."""
        from utils.error_handler import DatabaseError
        
        error = DatabaseError("DB error", details={"query": "SELECT 1"})
        assert error.error_code == "DB_ERROR"
    
    def test_validation_error_creation(self):
        """Test ValidationError creation."""
        from utils.error_handler import ValidationError
        
        error = ValidationError("Invalid data")
        assert error.error_code == "VALIDATION_ERROR"


# =============================================================================
# Authentication Tests
# =============================================================================

class TestAuthentication:
    """Tests for authentication module."""
    
    def test_auth_state_initialization(self):
        """Test authentication state initialization."""
        from utils.auth import init_auth_state
        
        # Mock session state
        class MockSessionState(dict):
            def __getattr__(self, key):
                return self.get(key)
            def __setattr__(self, key, value):
                self[key] = value
        
        mock_st = MagicMock()
        mock_st.session_state = MockSessionState()
        
        with patch('utils.auth.st', mock_st):
            init_auth_state()
            assert 'authenticated' in mock_st.session_state
    
    def test_is_email_allowed(self):
        """Test email allowance check."""
        from utils.auth import is_email_allowed
        
        # Without ALLOWED_EMAILS set, all should be allowed
        with patch.dict(os.environ, {}, clear=True):
            assert is_email_allowed("any@email.com") == True


# =============================================================================
# Performance Tests
# =============================================================================

class TestPerformance:
    """Tests for performance utilities."""
    
    def test_performance_monitor(self):
        """Test performance monitor."""
        from utils.performance import PerformanceMonitor
        
        monitor = PerformanceMonitor()
        monitor.record("test_metric", 0.5)
        monitor.record("test_metric", 1.0)
        
        stats = monitor.get_stats("test_metric")
        assert stats['count'] == 2
        assert stats['min'] == 0.5
        assert stats['max'] == 1.0
    
    def test_timed_decorator(self):
        """Test timing decorator."""
        from utils.performance import timed
        from utils.performance import get_performance_monitor
        import time
        
        @timed
        def quick_function():
            return 42
        
        result = quick_function()
        assert result == 42
        
        monitor = get_performance_monitor()
        stats = monitor.get_stats("quick_function")
        assert stats['count'] >= 1
    
    def test_memoize_decorator(self):
        """Test memoization decorator."""
        from utils.performance import memoize
        
        call_count = 0
        
        @memoize
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        assert expensive_function(5) == 10
        assert expensive_function(5) == 10  # Should use cached result
        assert call_count == 1  # Function only called once


# =============================================================================
# SQL Console Tests
# =============================================================================

class TestSQLConsole:
    """Tests for SQL console functionality."""
    
    def test_sql_console_manager_creation(self):
        """Test SQL console manager creation."""
        from utils.sql_console import create_sql_console_manager
        
        manager = create_sql_console_manager()
        assert manager is not None
    
    def test_sql_highlight_function(self):
        """Test SQL highlighting function."""
        from utils.sql_console import highlight_sql
        
        result = highlight_sql("SELECT * FROM users")
        assert "SELECT" in result
        assert "<span" in result  # Contains HTML span tags
    
    def test_query_type_badge_function(self):
        """Test query type badge function."""
        from utils.sql_console import get_query_type_badge
        
        badge = get_query_type_badge("aggregate")
        assert badge == "badge-aggregate"
        
        badge = get_query_type_badge("inner join")
        assert badge == "badge-join"
    
    def test_query_categories_defined(self):
        """Test that query categories are defined."""
        from utils.sql_console import QUERY_CATEGORIES
        
        assert isinstance(QUERY_CATEGORIES, dict)
        assert "Simple Queries" in QUERY_CATEGORIES
        assert "Aggregate Queries" in QUERY_CATEGORIES


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
