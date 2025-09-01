import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
from dotenv import load_dotenv
import requests
import json
from typing import List, Dict, Any
from services.ai_service import generate_flashcards_with_ai, validate_flashcard_quality
from utils.text_processing import preprocess_notes_for_ai
 
load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
CORS(app)

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_NAME', 'ai_study_buddy'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'port': int(os.environ.get('DB_PORT', 3306))
}

# Hugging Face API configuration
HF_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# API Routes
@app.route('/')
def hello():
    return {"message": "Welcome to AI Study Buddy!"}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/decks', methods=['GET'])
def get_decks():
    """Get all decks for a user"""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """SELECT d.id, d.title, d.description, d.created_at,
                      COUNT(f.id) as flashcard_count
               FROM decks d
               LEFT JOIN flashcards f ON d.id = f.deck_id
               GROUP BY d.id
               ORDER BY d.created_at DESC"""
        )
        decks = cursor.fetchall()
        
        return jsonify({"decks": decks})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/decks', methods=['POST'])
def create_deck():
    """Create a new deck with AI-generated flashcards"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('title', 'notes')):
        return jsonify({"error": "Missing title or notes"}), 400
    
    connection, cursor = None, None  
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500

        # ---- AI flashcard generation ----
        preprocessed_notes = preprocess_notes_for_ai(data['notes'])
        flashcards = generate_flashcards_with_ai(preprocessed_notes, 20)
        flashcards = validate_flashcard_quality(flashcards)
        
        # Ensure we have at least 3 flashcards
        if len(flashcards) < 3:
            return jsonify({"error": "Unable to generate sufficient flashcards from the provided notes"}), 400
        
        cursor = connection.cursor()

        # ---- Create deck ----
        cursor.execute(
            "INSERT INTO decks (title, description, original_notes) VALUES (%s, %s, %s)",
            (data['title'], data.get('description', ''), data['notes'])
        )
        deck_id = cursor.lastrowid
        
        # ---- Create flashcards ----
        for flashcard in flashcards:
            cursor.execute(
                "INSERT INTO flashcards (deck_id, question, answer, difficulty_level) VALUES (%s, %s, %s, %s)",
                (deck_id, flashcard['question'], flashcard['answer'], flashcard.get('difficulty_level', 'medium'))
            )
        
        connection.commit()
        
        return jsonify({
            "message": "Deck created successfully",
            "deck_id": deck_id,
            "flashcard_count": len(flashcards),
            "flashcards": flashcards  # Return generated flashcards for immediate preview
        }), 201
        
    except Exception as e:
        if connection:
            connection.rollback()
        print("❌ ERROR in create_deck:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route('/api/decks/<int:deck_id>/flashcards', methods=['GET'])
def get_flashcards(deck_id):
    """Get all flashcards for a specific deck"""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Verify deck exists
        cursor.execute(
            "SELECT id FROM decks WHERE id = %s",
            (deck_id,)
        )
        if not cursor.fetchone():
            return jsonify({"error": "Deck not found or access denied"}), 404
        
        # Get flashcards
        cursor.execute(
            "SELECT id, question, answer, difficulty_level FROM flashcards WHERE deck_id = %s ORDER BY id",
            (deck_id,)
        )
        flashcards = cursor.fetchall()
        
        return jsonify({"flashcards": flashcards})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/decks/<int:deck_id>', methods=['DELETE'])
def delete_deck(deck_id):
    """Delete a deck and all its flashcards"""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor()
        
        # Delete the deck
        cursor.execute(
            "DELETE FROM decks WHERE id = %s",
            (deck_id,)
        )
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Deck not found or access denied"}), 404
        
        connection.commit()
        return jsonify({"message": "Deck deleted successfully"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
