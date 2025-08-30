# AI Study Buddy Backend

Flask-based REST API for the AI Study Buddy flashcard generator.

## Features

- User authentication (registration/login)
- Deck management (create, read, delete)
- AI-powered flashcard generation using Hugging Face
- MySQL database integration
- RESTful API design

## Setup

1. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

2. Set up environment variables:
\`\`\`bash
cp .env.example .env
# Edit .env with your configuration
\`\`\`

3. Set up MySQL database:
\`\`\`bash
mysql -u root -p < ../scripts/database_schema.sql
\`\`\`

4. Run the application:
\`\`\`bash
python app.py
\`\`\`

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login

### Decks
- `GET /api/decks` - Get all user decks
- `POST /api/decks` - Create new deck with AI-generated flashcards
- `DELETE /api/decks/<id>` - Delete a deck

### Flashcards
- `GET /api/decks/<id>/flashcards` - Get flashcards for a deck

### Health
- `GET /api/health` - Health check

## Request/Response Examples

### Create Deck
\`\`\`json
POST /api/decks
{
  "title": "Biology Chapter 1",
  "description": "Cell structure and function",
  "notes": "Cells are the basic unit of life. They contain organelles like mitochondria, nucleus, and ribosomes..."
}

Response:
{
  "message": "Deck created successfully",
  "deck_id": 1,
  "flashcard_count": 5
}
\`\`\`

### Get Flashcards
\`\`\`json
GET /api/decks/1/flashcards

Response:
{
  "flashcards": [
    {
      "id": 1,
      "question": "What are the basic units of life?",
      "answer": "Cells",
      "difficulty_level": "medium"
    }
  ]
}
