import pytest
import json
from unittest.mock import patch, MagicMock

class TestHealthEndpoint:
    """Test the health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check returns 200 and correct response"""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data

class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    @patch('app.get_db_connection')
    def test_register_success(self, mock_get_db, client, mock_db_connection):
        """Test successful user registration"""
        mock_connection, mock_cursor = mock_db_connection
        mock_get_db.return_value = mock_connection
        mock_cursor.lastrowid = 1
        
        response = client.post('/api/auth/register', 
                             json={
                                 'username': 'testuser',
                                 'email': 'test@example.com',
                                 'password': 'password123'
                             })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User registered successfully'
        assert data['user_id'] == 1
    
    def test_register_missing_fields(self, client):
        """Test registration with missing fields"""
        response = client.post('/api/auth/register', 
                             json={'username': 'testuser'})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Missing required fields' in data['error']
    
    @patch('app.get_db_connection')
    def test_login_success(self, mock_get_db, client, mock_db_connection):
        """Test successful login"""
        mock_connection, mock_cursor = mock_db_connection
        mock_get_db.return_value = mock_connection
        
        # Mock user data
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Gm.F5.'  # 'password123'
        }
        
        with patch('werkzeug.security.check_password_hash', return_value=True):
            response = client.post('/api/auth/login',
                                 json={
                                     'username': 'testuser',
                                     'password': 'password123'
                                 })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Login successful'
        assert data['user']['username'] == 'testuser'

class TestDeckEndpoints:
    """Test deck management endpoints"""
    
    @patch('app.get_db_connection')
    def test_get_decks_unauthorized(self, mock_get_db, client):
        """Test getting decks without authentication"""
        response = client.get('/api/decks')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Authentication required' in data['error']
    
    @patch('app.get_db_connection')
    @patch('app.generate_flashcards_with_ai')
    def test_create_deck_success(self, mock_generate, mock_get_db, client, mock_db_connection, sample_flashcards):
        """Test successful deck creation"""
        mock_connection, mock_cursor = mock_db_connection
        mock_get_db.return_value = mock_connection
        mock_cursor.lastrowid = 1
        mock_generate.return_value = sample_flashcards
        
        # Simulate logged in user
        with client.session_transaction() as sess:
            sess['user_id'] = 1
        
        response = client.post('/api/decks',
                             json={
                                 'title': 'Test Deck',
                                 'description': 'Test Description',
                                 'notes': 'Test notes with enough content to generate flashcards'
                             })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Deck created successfully'
        assert data['deck_id'] == 1
        assert data['flashcard_count'] == 2
    
    def test_create_deck_missing_fields(self, client):
        """Test deck creation with missing fields"""
        with client.session_transaction() as sess:
            sess['user_id'] = 1
        
        response = client.post('/api/decks',
                             json={'title': 'Test Deck'})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Missing title or notes' in data['error']
    
    @patch('app.get_db_connection')
    def test_delete_deck_success(self, mock_get_db, client, mock_db_connection):
        """Test successful deck deletion"""
        mock_connection, mock_cursor = mock_db_connection
        mock_get_db.return_value = mock_connection
        mock_cursor.rowcount = 1
        
        with client.session_transaction() as sess:
            sess['user_id'] = 1
        
        response = client.delete('/api/decks/1')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Deck deleted successfully'
    
    @patch('app.get_db_connection')
    def test_delete_deck_not_found(self, mock_get_db, client, mock_db_connection):
        """Test deleting non-existent deck"""
        mock_connection, mock_cursor = mock_db_connection
        mock_get_db.return_value = mock_connection
        mock_cursor.rowcount = 0
        
        with client.session_transaction() as sess:
            sess['user_id'] = 1
        
        response = client.delete('/api/decks/999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Deck not found' in data['error']

class TestFlashcardEndpoints:
    """Test flashcard endpoints"""
    
    @patch('app.get_db_connection')
    def test_get_flashcards_success(self, mock_get_db, client, mock_db_connection, sample_flashcards):
        """Test getting flashcards for a deck"""
        mock_connection, mock_cursor = mock_db_connection
        mock_get_db.return_value = mock_connection
        
        # Mock deck ownership verification
        mock_cursor.fetchone.side_effect = [
            {'id': 1},  # Deck exists and user owns it
        ]
        
        # Mock flashcards data
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'question': 'What is the capital of France?',
                'answer': 'Paris',
                'difficulty_level': 'easy'
            }
        ]
        
        with client.session_transaction() as sess:
            sess['user_id'] = 1
        
        response = client.get('/api/decks/1/flashcards')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['flashcards']) == 1
        assert data['flashcards'][0]['question'] == 'What is the capital of France?'
    
    @patch('app.get_db_connection')
    def test_get_flashcards_deck_not_found(self, mock_get_db, client, mock_db_connection):
        """Test getting flashcards for non-existent deck"""
        mock_connection, mock_cursor = mock_db_connection
        mock_get_db.return_value = mock_connection
        mock_cursor.fetchone.return_value = None
        
        with client.session_transaction() as sess:
            sess['user_id'] = 1
        
        response = client.get('/api/decks/999/flashcards')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Deck not found' in data['error']
