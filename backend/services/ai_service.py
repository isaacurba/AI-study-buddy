import requests
import json
import re
from typing import List, Dict
import os
from dataclasses import dataclass
import nltk

# Make sure punkt is available for sentence splitting
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

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
        self.api_key = os.environ.get('HUGGINGFACE_API_KEY')
        self.base_url = "https://api-inference.huggingface.co/models"
        
        # Multiple model options
        self.models = {
            'text_generation': 'microsoft/DialoGPT-medium',
            'question_generation': 'valhalla/t5-small-qg-hl',
            'summarization': 'facebook/bart-large-cnn'
        }
        
        # ✅ Only set headers if API key exists
        self.headers = (
            {"Authorization": f"Bearer {self.api_key}"}
            if self.api_key else {}
        )
    
    def generate_flashcards(self, notes: str, count: int = 5) -> List[FlashcardPair]:
        """Generate flashcards using multiple AI strategies"""
        if not self.api_key:
            print("⚠️ Warning: No Hugging Face API key found, using fallback generation")
            return self._create_fallback_flashcards(notes, count)
        
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
            except requests.exceptions.HTTPError as e:
                print(f"❌ Hugging Face API error: {e} - {e.response.text}")
                continue
            except Exception as e:
                print(f"Strategy failed: {e}")
                continue
        
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
        sentences = self._split_into_sentences(notes)
        flashcards = []
        
        for sentence in sentences[:count]:
            if len(sentence.strip()) < 20:
                continue
                
            payload = {
                "inputs": f"generate question: {sentence}",
                "parameters": {"max_length": 100, "temperature": 0.8}
            }
            
            response = requests.post(
                f"{self.base_url}/{self.models['question_generation']}",
                headers=self.headers,
                json=payload,
                timeout=15
            )
            
            response.raise_for_status()
            result = response.json()
            question = result[0]['generated_text'] if result else ""
            
            if question and len(question) > 10:
                flashcards.append(FlashcardPair(
                    question=question.strip(),
                    answer=sentence.strip(),
                    confidence=0.8
                ))
        
        return flashcards
    
    def _generate_with_keyword_extraction(self, notes: str, count: int) -> List[FlashcardPair]:
        """Generate flashcards by extracting key concepts and creating questions"""
        key_concepts = self._extract_key_concepts(notes)
        sentences = self._split_into_sentences(notes)
        
        flashcards = []
        for concept in key_concepts[:count]:
            relevant_sentences = [s for s in sentences if concept.lower() in s.lower()]
            if relevant_sentences:
                context = relevant_sentences[0]
                templates = [
                    f"What is {concept}?",
                    f"Define {concept}.",
                    f"Explain the concept of {concept}.",
                    f"What do you know about {concept}?",
                    f"Describe {concept}."
                ]
                question = templates[len(flashcards) % len(templates)]
                flashcards.append(FlashcardPair(
                    question=question,
                    answer=context.strip(),
                    confidence=0.6
                ))
        return flashcards
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts and terms from text"""
        concepts = []
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        concepts.extend(capitalized)
        quoted = re.findall(r'"([^"]+)"', text)
        concepts.extend(quoted)
        parentheses = re.findall(r'\(([^)]+)\)', text)
        concepts.extend(parentheses)
        unique = list(set(concepts))
        return [c for c in unique if 2 < len(c) < 50]

    def _create_generation_prompt(self, notes: str, count: int) -> str:
        """Builds the text prompt for Hugging Face generation"""
        return (
            f"Generate {count} study flashcards in JSON format with fields 'question' and 'answer'. "
            f"Focus only on academic content. Context:\n{notes[:1000]}"
        )

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences safely"""
        try:
            return nltk.sent_tokenize(text)
        except Exception:
            return re.split(r'(?<=[.!?]) +', text)

    def _parse_generated_flashcards(self, generated_text: str) -> List[FlashcardPair]:
        """Parse raw text output into FlashcardPair list"""
        flashcards = []
        try:
            data = json.loads(generated_text)
            if isinstance(data, list):
                for item in data:
                    if "question" in item and "answer" in item:
                        flashcards.append(FlashcardPair(
                            question=item["question"],
                            answer=item["answer"],
                            confidence=0.7
                        ))
        except Exception:
            pass
        return flashcards

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
            words = sentence.split()
            if len(words) > 5:
                important_words = [w for w in words if len(w) > 4 and w.isalpha()]
                if important_words:
                    word_to_blank = important_words[0]
                    question = sentence.replace(word_to_blank, "______", 1)
                    
                    flashcards.append(FlashcardPair(
                        question=f"Fill in the blank: {question}",
                        answer=word_to_blank,
                        confidence=0.4
                    ))
        
        while len(flashcards) < count:
            flashcards.append(FlashcardPair(
                question=f"Review question {len(flashcards) + 1}",
                answer="Please review your study notes for this concept.",
                confidence=0.1
            ))
        
        return flashcards[:count]
    
    def assess_difficulty(self, question: str, answer: str) -> str:
        """Assess the difficulty level of a flashcard"""
        question_length = len(question.split())
        answer_length = len(answer.split())
        
        complex_words = ['analyze', 'evaluate', 'synthesize', 'compare', 'contrast']
        has_complex_words = any(word in question.lower() for word in complex_words)
        
        if has_complex_words or answer_length > 20:
            return "hard"
        elif question_length > 10 or answer_length > 10:
            return "medium"
        else:
            return "easy"


# ✅ Utility functions should be OUTSIDE the class
def generate_flashcards_with_ai(notes: str, count: int = 5) -> List[Dict[str, str]]:
    generator = AIFlashcardGenerator()
    flashcard_pairs = generator.generate_flashcards(notes, count)

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
        
        if len(question) < 5 or len(answer) < 3:
            continue
            
        if not any(existing['question'].lower() == question.lower() for existing in validated):
            validated.append(card)
    
    return validated
