"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { FlipCard } from "@/components/ui/flip-card"
import { ArrowLeft, ArrowRight, RotateCcw, CheckCircle, Shuffle } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { LoadingSpinner } from "@/components/ui/loading-spinner"

interface Flashcard {
  id: number
  question: string
  answer: string
  difficulty_level: "easy" | "medium" | "hard"
}

interface FlashcardGridProps {
  deckId: number
  onBackToDecks: () => void
}

export function FlashcardGrid({ deckId, onBackToDecks }: FlashcardGridProps) {
  const [flashcards, setFlashcards] = useState<Flashcard[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isFlipped, setIsFlipped] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [studiedCards, setStudiedCards] = useState<Set<number>>(new Set())
  const [isShuffled, setIsShuffled] = useState(false)
  const [originalOrder, setOriginalOrder] = useState<Flashcard[]>([])
  const { toast } = useToast()

  useEffect(() => {
    fetchFlashcards()
  }, [deckId])

  const fetchFlashcards = async () => {
    try {
      const response = await fetch(`/api/decks/${deckId}/flashcards`)
      if (response.ok) {
        const data = await response.json()
        const cards = data.flashcards || []
        setFlashcards(cards)
        setOriginalOrder(cards)
      } else {
        // Demo data for development
        const demoCards = [
          {
            id: 1,
            question: "What is the powerhouse of the cell?",
            answer:
              "The mitochondria is often called the powerhouse of the cell because it produces ATP (adenosine triphosphate), which provides energy for cellular processes.",
            difficulty_level: "easy" as const,
          },
          {
            id: 2,
            question: "What is the function of the cell membrane?",
            answer:
              "The cell membrane controls what enters and exits the cell, maintaining cellular homeostasis through selective permeability.",
            difficulty_level: "medium" as const,
          },
          {
            id: 3,
            question: "Describe the process of photosynthesis.",
            answer:
              "Photosynthesis is the process by which plants convert light energy, carbon dioxide, and water into glucose and oxygen using chlorophyll in the chloroplasts.",
            difficulty_level: "hard" as const,
          },
          {
            id: 4,
            question: "What is DNA and what does it contain?",
            answer:
              "DNA (Deoxyribonucleic acid) is the hereditary material that contains genetic instructions for the development and function of living organisms.",
            difficulty_level: "medium" as const,
          },
          {
            id: 5,
            question: "Explain the difference between prokaryotic and eukaryotic cells.",
            answer:
              "Prokaryotic cells lack a membrane-bound nucleus and organelles (like bacteria), while eukaryotic cells have a nucleus and membrane-bound organelles (like plant and animal cells).",
            difficulty_level: "hard" as const,
          },
        ]
        setFlashcards(demoCards)
        setOriginalOrder(demoCards)
      }
    } catch (error) {
      console.error("Error fetching flashcards:", error)
      toast({
        title: "Error Loading Flashcards",
        description: "Unable to load flashcards. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleNext = () => {
    if (currentIndex < flashcards.length - 1) {
      setCurrentIndex(currentIndex + 1)
      setIsFlipped(false)
    }
  }

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1)
      setIsFlipped(false)
    }
  }

  const handleFlip = () => {
    setIsFlipped(!isFlipped)
    if (!isFlipped) {
      setStudiedCards((prev) => new Set([...prev, flashcards[currentIndex].id]))
    }
  }

  const handleReset = () => {
    setCurrentIndex(0)
    setIsFlipped(false)
    setStudiedCards(new Set())
    if (isShuffled) {
      setFlashcards(originalOrder)
      setIsShuffled(false)
    }
  }

  const handleShuffle = () => {
    if (isShuffled) {
      // Restore original order
      setFlashcards(originalOrder)
      setIsShuffled(false)
      toast({
        title: "Cards Restored",
        description: "Flashcards are back in original order.",
      })
    } else {
      // Shuffle cards
      const shuffled = [...flashcards].sort(() => Math.random() - 0.5)
      setFlashcards(shuffled)
      setIsShuffled(true)
      toast({
        title: "Cards Shuffled",
        description: "Flashcards have been randomized for varied practice.",
      })
    }
    setCurrentIndex(0)
    setIsFlipped(false)
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "easy":
        return "bg-green-100 text-green-800 border-green-200"
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-200"
      case "hard":
        return "bg-red-100 text-red-800 border-red-200"
      default:
        return "bg-gray-100 text-gray-800 border-gray-200"
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (flashcards.length === 0) {
    return (
      <Card className="text-center py-12">
        <CardContent>
          <div className="space-y-4">
            <h3 className="text-xl font-semibold text-foreground">No Flashcards Found</h3>
            <p className="text-muted-foreground">This deck doesn't contain any flashcards yet.</p>
            <Button onClick={onBackToDecks}>Back to Decks</Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  const currentCard = flashcards[currentIndex]
  const progress = ((currentIndex + 1) / flashcards.length) * 100
  const studiedProgress = (studiedCards.size / flashcards.length) * 100

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Button variant="ghost" onClick={onBackToDecks} className="gap-2">
          <ArrowLeft className="h-4 w-4" />
          Back to Decks
        </Button>
        <div className="flex items-center gap-4">
          <Badge variant="outline" className="gap-1">
            <CheckCircle className="h-3 w-3" />
            {studiedCards.size} studied
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={handleShuffle}
            className={`gap-2 bg-transparent ${isShuffled ? "text-primary border-primary" : ""}`}
          >
            <Shuffle className="h-4 w-4" />
            {isShuffled ? "Restore Order" : "Shuffle"}
          </Button>
          <Button variant="outline" size="sm" onClick={handleReset} className="gap-2 bg-transparent">
            <RotateCcw className="h-4 w-4" />
            Reset
          </Button>
        </div>
      </div>

      {/* Progress */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm text-muted-foreground">
          <span>
            Card {currentIndex + 1} of {flashcards.length}
            {isShuffled && <span className="text-primary ml-2">(Shuffled)</span>}
          </span>
          <span>{Math.round(studiedProgress)}% studied</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      {/* Flashcard */}
      <FlipCard
        question={currentCard.question}
        answer={currentCard.answer}
        difficulty={currentCard.difficulty_level}
        isFlipped={isFlipped}
        onFlip={handleFlip}
      />

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          onClick={handlePrevious}
          disabled={currentIndex === 0}
          className="gap-2 bg-transparent"
        >
          <ArrowLeft className="h-4 w-4" />
          Previous
        </Button>

        <div className="flex items-center gap-2">
          {flashcards.map((_, index) => (
            <button
              key={index}
              onClick={() => {
                setCurrentIndex(index)
                setIsFlipped(false)
              }}
              className={`w-3 h-3 rounded-full transition-colors ${
                index === currentIndex
                  ? "bg-primary"
                  : studiedCards.has(flashcards[index].id)
                    ? "bg-emerald-500"
                    : "bg-muted"
              }`}
              aria-label={`Go to card ${index + 1}`}
            />
          ))}
        </div>

        <Button
          variant="outline"
          onClick={handleNext}
          disabled={currentIndex === flashcards.length - 1}
          className="gap-2 bg-transparent"
        >
          Next
          <ArrowRight className="h-4 w-4" />
        </Button>
      </div>

      {/* Study completion */}
      {studiedCards.size === flashcards.length && (
        <Card className="bg-emerald-50 border-emerald-200 dark:bg-emerald-900/20 dark:border-emerald-800">
          <CardContent className="pt-6 text-center">
            <div className="space-y-2">
              <CheckCircle className="h-8 w-8 text-emerald-600 mx-auto" />
              <h3 className="text-lg font-semibold text-emerald-800 dark:text-emerald-400">
                Congratulations! You've studied all cards!
              </h3>
              <p className="text-emerald-700 dark:text-emerald-300">
                Great job completing this deck. Ready to study another one?
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
