import requests
import json
import re
from typing import List, Dict, Any, Optional
import os
from dataclasses import dataclass

@dataclass
class FlashcardPair:
    """Data class for flashcard question-answer pairs"""
    question: str
    answer: str
    difficulty: str = "medium"
    confidence: float = 0.0

class AIFlashcardGenerator:
    """Enhanced AI service for generating flashcards using Hugging Face API"""
    
    def __init__(self):
        self.api_key = os.environ.get('HUGGING_FACE_API_KEY')
        self.base_url = "https://api-inference.huggingface.co/models"
        
        # Multiple model options for different approaches
        self.models = {
            'text_generation': 'microsoft/DialoGPT-medium',
            'question_generation': 'valhalla/t5-small-qg-hl',
            'summarization': 'facebook/bart-large-cnn'
        }
        
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    def generate_flashcards(self, notes: str, count: int = 5) -> List[FlashcardPair]:
        """
        Generate flashcards using multiple AI strategies
        
        Args:
            notes: Input study notes
            count: Number of flashcards to generate
            
        Returns:
            List of FlashcardPair objects
        """
        if not self.api_key:
            print("Warning: No Hugging Face API key found, using fallback generation")
            return self._create_fallback_flashcards(notes, count)
        
        # Try multiple generation strategies
        strategies = [
            self._generate_with_text_generation,
            self._generate_with_question_generation,
            self._generate_with_keyword_extraction
        ]
        
        for strategy in strategies:
            try:
                flashcards = strategy(notes, count)
                if len(flashcards) >= count:
                    return flashcards[:count]
            except Exception as e:
                print(f"Strategy failed: {e}")
                continue
        
        # Fallback to rule-based generation
        return self._create_fallback_flashcards(notes, count)
    
    def _generate_with_text_generation(self, notes: str, count: int) -> List[FlashcardPair]:
        """Generate flashcards using text generation model"""
        prompt = self._create_generation_prompt(notes, count)
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 400,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        response = requests.post(
            f"{self.base_url}/{self.models['text_generation']}",
            headers=self.headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        generated_text = result[0]['generated_text'] if result else ""
        
        return self._parse_generated_flashcards(generated_text)
    
    def _generate_with_question_generation(self, notes: str, count: int) -> List[FlashcardPair]:
        """Generate questions using specialized question generation model"""
        # Split notes into sentences for individual question generation
        sentences = self._split_into_sentences(notes)
        flashcards = []
        
        for sentence in sentences[:count]:
            if len(sentence.strip()) < 20:  # Skip very short sentences
                continue
                
            try:
                payload = {
                    "inputs": f"generate question: {sentence}",
                    "parameters": {
                        "max_length": 100,
                        "temperature": 0.8
                    }
                }
                
                response = requests.post(
                    f"{self.base_url}/{self.models['question_generation']}",
                    headers=self.headers,
                    json=payload,
                    timeout=15
                )
                
                if response.status_code == 200:
                    result = response.json()
                    question = result[0]['generated_text'] if result else ""
                    
                    if question and len(question) > 10:
                        flashcards.append(FlashcardPair(
                            question=question.strip(),
                            answer=sentence.strip(),
                            confidence=0.8
                        ))
                        
            except Exception as e:
                print(f"Question generation failed for sentence: {e}")
                continue
        
        return flashcards
    
    def _generate_with_keyword_extraction(self, notes: str, count: int) -> List[FlashcardPair]:
        """Generate flashcards by extracting key concepts and creating questions"""
        # Extract key terms and concepts
        key_concepts = self._extract_key_concepts(notes)
        sentences = self._split_into_sentences(notes)
        
        flashcards = []
        
        for concept in key_concepts[:count]:
            # Find sentences containing this concept
            relevant_sentences = [s for s in sentences if concept.lower() in s.lower()]
            
            if relevant_sentences:
                context = relevant_sentences[0]
                question_templates = [
                    f"What is {concept}?",
                    f"Define {concept}.",
                    f"Explain the concept of {concept}.",
                    f"What do you know about {concept}?",
                    f"Describe {concept}."
                ]
                
                question = question_templates[len(flashcards) % len(question_templates)]
                
                flashcards.append(FlashcardPair(
                    question=question,
                    answer=context.strip(),
                    confidence=0.6
                ))
        
        return flashcards
    
    def _create_generation_prompt(self, notes: str, count: int) -> str:
        """Create an optimized prompt for flashcard generation"""
        return f"""
Create {count} educational flashcards from these study notes. Format each as:

Q: [Clear, specific question]
A: [Concise, accurate answer]

Study Notes:
{notes[:1000]}  # Limit input length

Generate {count} flashcards now:
"""
    
    def _parse_generated_flashcards(self, text: str) -> List[FlashcardPair]:
        """Parse AI-generated text into structured flashcards"""
        flashcards = []
        
        # Multiple parsing patterns
        patterns = [
            r'Q:\s*(.+?)\s*A:\s*(.+?)(?=Q:|$)',
            r'Question:\s*(.+?)\s*Answer:\s*(.+?)(?=Question:|$)',
            r'(\d+)\.\s*Q:\s*(.+?)\s*A:\s*(.+?)(?=\d+\.|$)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                if len(match) == 2:  # Q&A pair
                    question, answer = match
                elif len(match) == 3:  # Numbered Q&A
                    _, question, answer = match
                else:
                    continue
                
                question = question.strip()
                answer = answer.strip()
                
                if len(question) > 5 and len(answer) > 5:
                    flashcards.append(FlashcardPair(
                        question=question,
                        answer=answer,
                        confidence=0.7
                    ))
        
        return flashcards
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences for processing"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 20]
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts and terms from text"""
        # Simple keyword extraction using capitalized words and common patterns
        concepts = []
        
        # Find capitalized words (potential proper nouns/concepts)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        concepts.extend(capitalized)
        
        # Find quoted terms
        quoted = re.findall(r'"([^"]+)"', text)
        concepts.extend(quoted)
        
        # Find terms in parentheses
        parentheses = re.findall(r'$$([^)]+)$$', text)
        concepts.extend(parentheses)
        
        # Remove duplicates and filter
        unique_concepts = list(set(concepts))
        return [c for c in unique_concepts if 2 < len(c) < 50]
    
    def _create_fallback_flashcards(self, notes: str, count: int) -> List[FlashcardPair]:
        """Create basic flashcards when AI generation fails"""
        sentences = self._split_into_sentences(notes)
        key_concepts = self._extract_key_concepts(notes)
        
        flashcards = []
        
        # Create flashcards from key concepts
        for i, concept in enumerate(key_concepts[:count//2]):
            relevant_sentences = [s for s in sentences if concept.lower() in s.lower()]
            context = relevant_sentences[0] if relevant_sentences else f"This relates to {concept}"
            
            flashcards.append(FlashcardPair(
                question=f"What is {concept}?",
                answer=context,
                confidence=0.3
            ))
        
        # Create flashcards from sentences
        remaining_count = count - len(flashcards)
        for sentence in sentences[:remaining_count]:
            # Create a question by replacing key terms with blanks
            words = sentence.split()
            if len(words) > 5:
                # Find important words to blank out
                important_words = [w for w in words if len(w) > 4 and w.isalpha()]
                if important_words:
                    word_to_blank = important_words[0]
                    question = sentence.replace(word_to_blank, "______", 1)
                    
                    flashcards.append(FlashcardPair(
                        question=f"Fill in the blank: {question}",
                        answer=word_to_blank,
                        confidence=0.4
                    ))
        
        # Ensure we have enough flashcards
        while len(flashcards) < count:
            flashcards.append(FlashcardPair(
                question=f"Review question {len(flashcards) + 1}",
                answer="Please review your study notes for this concept.",
                confidence=0.1
            ))
        
        return flashcards[:count]
    
    def assess_difficulty(self, question: str, answer: str) -> str:
        """Assess the difficulty level of a flashcard"""
        # Simple heuristic-based difficulty assessment
        question_length = len(question.split())
        answer_length = len(answer.split())
        
        # Check for complexity indicators
        complex_words = ['analyze', 'evaluate', 'synthesize', 'compare', 'contrast']
        has_complex_words = any(word in question.lower() for word in complex_words)
        
        if has_complex_words or answer_length > 20:
            return "hard"
        elif question_length > 10 or answer_length > 10:
            return "medium"
        else:
            return "easy"

# Utility functions for the main app
def generate_flashcards_with_ai(notes: str, count: int = 5) -> List[Dict[str, str]]:
    """
    Main function to generate flashcards - used by Flask app
    
    Args:
        notes: Study notes text
        count: Number of flashcards to generate
        
    Returns:
        List of dictionaries with question, answer, and difficulty
    """
    generator = AIFlashcardGenerator()
    flashcard_pairs = generator.generate_flashcards(notes, count)
    
    # Convert to dictionary format for JSON serialization
    flashcards = []
    for pair in flashcard_pairs:
        difficulty = generator.assess_difficulty(pair.question, pair.answer)
        flashcards.append({
            "question": pair.question,
            "answer": pair.answer,
            "difficulty_level": difficulty,
            "confidence": pair.confidence
        })
    
    return flashcards

def validate_flashcard_quality(flashcards: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Validate and improve flashcard quality"""
    validated = []
    
    for card in flashcards:
        question = card.get('question', '').strip()
        answer = card.get('answer', '').strip()
        
        # Quality checks
        if len(question) < 5 or len(answer) < 3:
            continue
            
        # Remove duplicates
        if not any(existing['question'].lower() == question.lower() for existing in validated):
            validated.append(card)
    
    return validated
