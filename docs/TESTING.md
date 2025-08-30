# Testing Guide for AI Study Buddy

This document provides comprehensive testing guidance for both frontend and backend components of the AI Study Buddy application.

## Frontend Testing (Jest + React Testing Library)

### Setup

The frontend uses Jest with React Testing Library for unit and integration testing.

#### Key Dependencies
- `@testing-library/react` - React component testing utilities
- `@testing-library/jest-dom` - Custom Jest matchers
- `@testing-library/user-event` - User interaction simulation
- `jest` - Testing framework
- `jest-environment-jsdom` - DOM environment for tests

### Running Tests

\`\`\`bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run tests for CI (no watch mode)
npm run test:ci
\`\`\`

### Test Structure

Tests are organized in the `__tests__` directory with the following structure:
\`\`\`
__tests__/
├── components/
│   ├── flip-card.test.tsx
│   ├── note-input.test.tsx
│   └── deck-list.test.tsx
├── hooks/
│   └── use-toast.test.tsx
└── utils/
    └── api.test.tsx
\`\`\`

### Writing Tests

#### Component Testing Example

\`\`\`typescript
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FlipCard } from '@/components/ui/flip-card'

describe('FlipCard', () => {
  const mockProps = {
    question: 'Test question?',
    answer: 'Test answer',
    difficulty: 'easy' as const,
    isFlipped: false,
    onFlip: jest.fn(),
  }

  it('renders question when not flipped', () => {
    render(<FlipCard {...mockProps} />)
    expect(screen.getByText('Test question?')).toBeInTheDocument()
  })

  it('calls onFlip when clicked', async () => {
    const user = userEvent.setup()
    render(<FlipCard {...mockProps} />)
    
    await user.click(screen.getByText('Test question?'))
    expect(mockProps.onFlip).toHaveBeenCalled()
  })
})
\`\`\`

### Best Practices

1. **Test user interactions, not implementation details**
2. **Use semantic queries** (`getByRole`, `getByLabelText`)
3. **Mock external dependencies** (APIs, third-party libraries)
4. **Test accessibility** (ARIA attributes, keyboard navigation)
5. **Maintain good coverage** (aim for 70%+ coverage)

## Backend Testing (pytest)

### Setup

The backend uses pytest for unit and integration testing.

#### Key Dependencies
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities
- `requests-mock` - HTTP request mocking
- `factory-boy` - Test data generation

### Running Tests

\`\`\`bash
# Run all backend tests
npm run test:backend

# Run tests in watch mode
npm run test:backend:watch

# Run tests with coverage
npm run test:backend:coverage

# Run specific test file
cd backend && python -m pytest tests/test_api_endpoints.py

# Run tests with verbose output
cd backend && python -m pytest -v
\`\`\`

### Test Structure

Backend tests are organized in the `backend/tests/` directory:
\`\`\`
backend/tests/
├── conftest.py              # Test configuration and fixtures
├── test_api_endpoints.py    # API endpoint tests
├── test_ai_service.py       # AI service tests
└── test_utils.py           # Utility function tests
\`\`\`

### Writing Tests

#### API Endpoint Testing Example

\`\`\`python
import pytest
from unittest.mock import patch

class TestDeckEndpoints:
    @patch('app.get_db_connection')
    def test_create_deck_success(self, mock_get_db, client, mock_db_connection):
        mock_connection, mock_cursor = mock_db_connection
        mock_get_db.return_value = mock_connection
        
        with client.session_transaction() as sess:
            sess['user_id'] = 1
        
        response = client.post('/api/decks', json={
            'title': 'Test Deck',
            'notes': 'Test notes content'
        })
        
        assert response.status_code == 201
        assert 'deck_id' in response.json
\`\`\`

### Test Configuration

The `conftest.py` file contains shared fixtures:

\`\`\`python
@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    from app import app
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_db_connection():
    """Mock database connection for testing"""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    return mock_connection, mock_cursor
\`\`\`

## Continuous Integration (CI)

### GitHub Actions Workflow

The CI pipeline runs on every push and pull request:

1. **Frontend Tests**
   - Runs on Node.js 18.x and 20.x
   - Executes linting, type checking, and tests
   - Generates coverage reports

2. **Backend Tests**
   - Runs on Python 3.9, 3.10, and 3.11
   - Sets up MySQL test database
   - Executes pytest with coverage

3. **Security Scanning**
   - Runs Trivy vulnerability scanner
   - Uploads results to GitHub Security tab

4. **Build and Deploy**
   - Builds the application
   - Deploys to Vercel (on main branch)

### Coverage Requirements

- **Frontend**: Minimum 70% coverage for branches, functions, lines, and statements
- **Backend**: Minimum 80% coverage for all modules

### Running CI Locally

\`\`\`bash
# Run all tests (frontend + backend)
npm run test:all

# Check if build passes
npm run build

# Run linting
npm run lint
\`\`\`

## Test Data Management

### Frontend Test Data

Use factory functions for consistent test data:

\`\`\`typescript
const createMockDeck = (overrides = {}) => ({
  id: 1,
  title: 'Test Deck',
  description: 'Test Description',
  flashcard_count: 5,
  created_at: '2024-01-15T10:30:00Z',
  ...overrides,
})
\`\`\`

### Backend Test Data

Use pytest fixtures and factory-boy for test data:

\`\`\`python
@pytest.fixture
def sample_deck():
    return {
        'title': 'Biology Chapter 1',
        'description': 'Cell structure',
        'notes': 'Cells are the basic unit of life...'
    }
\`\`\`

## Debugging Tests

### Frontend Debugging

\`\`\`bash
# Run specific test file
npm test -- flip-card.test.tsx

# Run tests with debug output
npm test -- --verbose

# Run single test
npm test -- --testNamePattern="renders question when not flipped"
\`\`\`

### Backend Debugging

\`\`\`bash
# Run with debug output
cd backend && python -m pytest -v -s

# Run specific test
cd backend && python -m pytest tests/test_api_endpoints.py::TestDeckEndpoints::test_create_deck_success

# Run with pdb debugger
cd backend && python -m pytest --pdb
\`\`\`

## Performance Testing

### Load Testing (Optional)

For production deployments, consider adding load tests:

\`\`\`python
# backend/tests/test_performance.py
import pytest
import time
from concurrent.futures import ThreadPoolExecutor

def test_api_performance(client):
    """Test API response times under load"""
    def make_request():
        return client.get('/api/health')
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(100)]
        responses = [f.result() for f in futures]
    
    end_time = time.time()
    
    # All requests should succeed
    assert all(r.status_code == 200 for r in responses)
    
    # Should complete within reasonable time
    assert end_time - start_time < 5.0
\`\`\`

## Troubleshooting

### Common Issues

1. **Tests failing due to async operations**
   - Use `waitFor` from React Testing Library
   - Properly mock async functions

2. **Database connection issues in backend tests**
   - Ensure test database is properly configured
   - Use transaction rollback for test isolation

3. **Mock not working as expected**
   - Check mock placement (before imports)
   - Verify mock is being called correctly

4. **Coverage not meeting requirements**
   - Add tests for uncovered branches
   - Remove dead code
   - Add integration tests

### Getting Help

- Check test output for specific error messages
- Review the test configuration in `jest.config.js` and `conftest.py`
- Ensure all dependencies are installed
- Verify environment variables are set correctly for tests
