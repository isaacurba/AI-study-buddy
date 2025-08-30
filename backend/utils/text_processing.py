"""Text processing utilities for better flashcard generation"""

import re
from typing import List, Dict, Tuple
import nltk
from collections import Counter

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

class TextProcessor:
    """Advanced text processing for better flashcard generation"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        
        # Academic keywords that indicate important concepts
        self.academic_keywords = {
            'definition': ['define', 'definition', 'meaning', 'refers to', 'is defined as'],
            'process': ['process', 'procedure', 'method', 'steps', 'stages'],
            'cause_effect': ['because', 'therefore', 'as a result', 'leads to', 'causes'],
            'comparison': ['compared to', 'unlike', 'similar to', 'different from'],
            'importance': ['important', 'significant', 'crucial', 'essential', 'key']
        }
    
    def extract_key_sentences(self, text: str, max_sentences: int = 10) -> List[str]:
        """Extract the most important sentences from text"""
        sentences = sent_tokenize(text)
        
        # Score sentences based on various factors
        sentence_scores = []
        
        for sentence in sentences:
            score = self._score_sentence(sentence, text)
            sentence_scores.append((sentence, score))
        
        # Sort by score and return top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        return [sent for sent, score in sentence_scores[:max_sentences]]
    
    def _score_sentence(self, sentence: str, full_text: str) -> float:
        """Score a sentence based on its importance for flashcard generation"""
        score = 0.0
        
        # Length factor (prefer medium-length sentences)
        words = word_tokenize(sentence.lower())
        if 5 <= len(words) <= 25:
            score += 1.0
        elif len(words) < 5:
            score -= 0.5
        
        # Academic keyword presence
        sentence_lower = sentence.lower()
        for category, keywords in self.academic_keywords.items():
            for keyword in keywords:
                if keyword in sentence_lower:
                    score += 0.5
        
        # Capitalized words (potential proper nouns/concepts)
        capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', sentence)
        score += len(capitalized_words) * 0.2
        
        # Numbers and dates (often important facts)
        numbers = re.findall(r'\b\d+\b', sentence)
        score += len(numbers) * 0.3
        
        # Question-like structure (already formatted for flashcards)
        if sentence.strip().endswith('?'):
            score += 0.5
        
        return score
    
    def extract_concept_definitions(self, text: str) -> List[Dict[str, str]]:
        """Extract concept-definition pairs from text"""
        definitions = []
        sentences = sent_tokenize(text)
        
        # Patterns for definitions
        definition_patterns = [
            r'(.+?)\s+is\s+(.+?)(?:\.|$)',
            r'(.+?)\s+refers to\s+(.+?)(?:\.|$)',
            r'(.+?)\s+means\s+(.+?)(?:\.|$)',
            r'(.+?)\s+is defined as\s+(.+?)(?:\.|$)',
            r'(.+?):\s+(.+?)(?:\.|$)'
        ]
        
        for sentence in sentences:
            for pattern in definition_patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    concept, definition = match
                    concept = concept.strip()
                    definition = definition.strip()
                    
                    # Filter out overly long or short concepts
                    if 2 <= len(concept.split()) <= 5 and len(definition) > 10:
                        definitions.append({
                            'concept': concept,
                            'definition': definition,
                            'question': f"What is {concept}?",
                            'answer': definition
                        })
        
        return definitions
    
    def extract_process_steps(self, text: str) -> List[Dict[str, str]]:
        """Extract process steps that can become flashcards"""
        steps = []
        sentences = sent_tokenize(text)
        
        # Look for numbered steps or sequential indicators
        step_patterns = [
            r'(\d+)\.\s+(.+?)(?:\.|$)',
            r'(First|Second|Third|Fourth|Fifth|Next|Then|Finally),?\s+(.+?)(?:\.|$)',
            r'(Step \d+):\s+(.+?)(?:\.|$)'
        ]
        
        for sentence in sentences:
            for pattern in step_patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    step_indicator, step_content = match
                    
                    steps.append({
                        'step': step_indicator,
                        'content': step_content.strip(),
                        'question': f"What happens in {step_indicator.lower()}?",
                        'answer': step_content.strip()
                    })
        
        return steps
    
    def identify_question_types(self, text: str) -> Dict[str, List[str]]:
        """Identify what types of questions can be generated from the text"""
        question_types = {
            'factual': [],      # What, when, where questions
            'conceptual': [],   # Why, how questions
            'analytical': [],   # Compare, analyze questions
            'application': []   # Apply, use questions
        }
        
        sentences = sent_tokenize(text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Factual questions (definitions, facts)
            if any(word in sentence_lower for word in ['is', 'are', 'was', 'were', 'called']):
                question_types['factual'].append(sentence)
            
            # Conceptual questions (explanations, reasons)
            if any(word in sentence_lower for word in ['because', 'since', 'due to', 'reason']):
                question_types['conceptual'].append(sentence)
            
            # Analytical questions (comparisons, relationships)
            if any(word in sentence_lower for word in ['compared', 'unlike', 'similar', 'different']):
                question_types['analytical'].append(sentence)
            
            # Application questions (examples, uses)
            if any(word in sentence_lower for word in ['example', 'used for', 'applied', 'practice']):
                question_types['application'].append(sentence)
        
        return question_types
    
    def generate_question_stems(self, concept: str, context: str) -> List[str]:
        """Generate various question stems for a given concept"""
        stems = [
            f"What is {concept}?",
            f"Define {concept}.",
            f"Explain {concept}.",
            f"Describe {concept}.",
            f"What do you know about {concept}?",
            f"How would you explain {concept}?",
            f"What are the key features of {concept}?",
            f"Why is {concept} important?",
            f"How does {concept} work?",
            f"What is the purpose of {concept}?"
        ]
        
        # Context-specific stems
        context_lower = context.lower()
        if 'process' in context_lower:
            stems.extend([
                f"What are the steps in {concept}?",
                f"How does the {concept} process work?",
                f"What happens during {concept}?"
            ])
        
        if 'function' in context_lower or 'role' in context_lower:
            stems.extend([
                f"What is the function of {concept}?",
                f"What role does {concept} play?",
                f"How does {concept} contribute to...?"
            ])
        
        return stems

def preprocess_notes_for_ai(notes: str) -> str:
    """Preprocess notes to improve AI generation quality"""
    processor = TextProcessor()
    
    # Extract key sentences
    key_sentences = processor.extract_key_sentences(notes, max_sentences=15)
    
    # Join key sentences
    processed_notes = ' '.join(key_sentences)
    
    # Clean up text
    processed_notes = re.sub(r'\s+', ' ', processed_notes)  # Multiple spaces
    processed_notes = re.sub(r'\n+', ' ', processed_notes)  # Multiple newlines
    
    return processed_notes.strip()
