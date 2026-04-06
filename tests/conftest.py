"""
FitSense AI Dashboard - conftest.py
=====================================
Pytest configuration and shared fixtures.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def project_root_path():
    """Get project root path."""
    return project_root


@pytest.fixture(scope="session")
def sample_user_data():
    """Sample user data for testing."""
    return [
        {"user_id": 1, "username": "john_doe", "age": 28, "activity_level": "very_active"},
        {"user_id": 2, "username": "jane_smith", "age": 35, "activity_level": "moderately_active"},
        {"user_id": 3, "username": "bob_wilson", "age": 42, "activity_level": "sedentary"},
    ]


@pytest.fixture(scope="session")
def sample_workout_data():
    """Sample workout data for testing."""
    return [
        {"workout_id": 1, "user_id": 1, "duration_minutes": 45, "calories_burned": 350},
        {"workout_id": 2, "user_id": 1, "duration_minutes": 60, "calories_burned": 420},
        {"workout_id": 3, "user_id": 2, "duration_minutes": 30, "calories_burned": 200},
    ]
