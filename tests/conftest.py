"""
Pytest configuration and fixtures for testing the FastAPI app.
"""

import pytest
from fastapi.testclient import TestClient
from copy import deepcopy


# Import the app and activities
from src.app import app, activities


# Store the initial state of activities
INITIAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture
def client():
    """
    Provide a TestClient instance for making requests to the app.
    Resets the activities dict before each test to ensure test isolation.
    """
    # Reset activities to initial state before each test
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))
    
    return TestClient(app)
