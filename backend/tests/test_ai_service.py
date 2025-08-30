import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.ai_service import AIFlashcardGenerator, generate_flashcards_with_ai, FlashcardPair

class TestAIFlashcardGenerator(unittest.TestCase):
    """Test cases for AI flashcard generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = AIFlashcardGenerator()
        self.sample_notes = """
        Photosynthesis is the process by which plants convert sunlight into energy.
        Chlorophyll is the green pigment that captures light energy.
        The process occurs in the chloroplasts of plant cells.
        Carbon dioxide and water are the raw materials for photosynthesis.
        Oxygen is released as a byproduct of this process.
        """
    
    def test_fallback_flashcard_generation(self):
        """Test fallback flashcard generation when AI is unavailable"""
        flashcards = self.generator._create_fallback_flashcards(self.sample_notes, 5)
        
        self.assertEqual(len(flashcards), 5)
        self.assertIsInstance(flashcards[0], FlashcardPair)
        self.assertTrue(len(flashcards[0].question) > 0)
        self.assertTrue(len(flashcards[0].answer) > 0)
    
    def test_sentence_splitting(self):
        """Test sentence splitting functionality"""
        sentences = self.generator._split_into_sentences(self.sample_notes)
        
        self.assertGreater(len(sentences), 0)
        self.assertTrue(all(len(s) > 20 for s in sentences))
    
    def test_key_concept_extraction(self):
        """Test key concept extraction"""
        concepts = self.generator._extract_key_concepts(self.sample_notes)
        
        self.assertIn('Photosynthesis', concepts)
        self.assertIn('Chlorophyll', concepts)
    
    def test_difficulty_assessment(self):
        """Test difficulty level assessment"""
        easy_q = "What is photosynthesis?"
        easy_a = "A process in plants"
        
        hard_q = "Analyze the complex biochemical pathways involved in photosynthesis"
        hard_a = "Photosynthesis involves multiple complex biochemical reactions..."
        
        easy_difficulty = self.generator.assess_difficulty(easy_q, easy_a)
        hard_difficulty = self.generator.assess_difficulty(hard_q, hard_a)
        
        self.assertEqual(easy_difficulty, "easy")
        self.assertEqual(hard_difficulty, "hard")
    
    @patch('requests.post')
    def test_ai_generation_with_mock(self, mock_post):
        """Test AI generation with mocked API response"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            'generated_text': 'Q: What is photosynthesis? A: The process by which plants make food.'
        }]
        mock_post.return_value = mock_response
        
        # Set API key for this test
        self.generator.api_key = "test_key"
        
        flashcards = self.generator._generate_with_text_generation(self.sample_notes, 1)
        
        self.assertGreater(len(flashcards), 0)
        mock_post.assert_called_once()
    
    def test_flashcard_parsing(self):
        """Test parsing of generated flashcard text"""
        generated_text = """
        Q: What is photosynthesis?
        A: The process by which plants convert sunlight into energy.
        
        Q: What is chlorophyll?
        A: The green pigment that captures light energy.
        """
        
        flashcards = self.generator._parse_generated_flashcards(generated_text)
        
        self.assertEqual(len(flashcards), 2)
        self.assertEqual(flashcards[0].question, "What is photosynthesis?")
        self.assertIn("sunlight", flashcards[0].answer)

class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def test_generate_flashcards_with_ai(self):
        """Test main generation function"""
        notes = "The mitochondria is the powerhouse of the cell."
        flashcards = generate_flashcards_with_ai(notes, 3)
        
        self.assertEqual(len(flashcards), 3)
        self.assertIn('question', flashcards[0])
        self.assertIn('answer', flashcards[0])
        self.assertIn('difficulty_level', flashcards[0])

if __name__ == '__main__':
    unittest.main()
