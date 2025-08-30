import pytest
import sys
import os
from unittest.mock import MagicMock

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture
def mock_db_connection():
    """Mock database connection for testing"""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.is_connected.return_value = True
    return mock_connection, mock_cursor

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    from app import app
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def sample_flashcards():
    """Sample flashcard data for testing"""
    return [
        {
            "question": "What is the capital of France?",
            "answer": "Paris",
            "difficulty_level": "easy"
        },
        {
            "question": "What is photosynthesis?",
            "answer": "The process by which plants convert sunlight into energy",
            "difficulty_level": "medium"
        }
    ]

@pytest.fixture
def sample_notes():
    """Sample study notes for testing"""
    return """
    Photosynthesis is the process by which plants convert sunlight into energy.
    Chlorophyll is the green pigment that captures light energy.
    The process occurs in the chloroplasts of plant cells.
    Carbon dioxide and water are the raw materials for photosynthesis.
    Oxygen is released as a byproduct of this process.
    """
