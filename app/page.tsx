"use client"

import { useState } from "react"
import { Header } from "@/components/layout/header"
import { NoteInput } from "@/components/note-input"
import { DeckList } from "@/components/deck-list"
import { FlashcardGrid } from "@/components/flashcard-grid"
import { LoadingSpinner } from "@/components/ui/loading-spinner"
import { useToast } from "@/hooks/use-toast"

export default function HomePage() {
  const [currentView, setCurrentView] = useState<"home" | "create" | "study">("home")
  const [selectedDeckId, setSelectedDeckId] = useState<number | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const { toast } = useToast()

  const handleCreateDeck = () => {
    setCurrentView("create")
  }

  const handleStudyDeck = (deckId: number) => {
    setSelectedDeckId(deckId)
    setCurrentView("study")
  }

  const handleBackToHome = () => {
    setCurrentView("home")
    setSelectedDeckId(null)
  }

  const handleDeckCreated = () => {
    setCurrentView("home")
    toast({
      title: "Success!",
      description: "Your flashcard deck has been created successfully.",
    })
  }

  return (
    <div className="min-h-screen bg-background">
      <Header currentView={currentView} onBackToHome={handleBackToHome} onCreateDeck={handleCreateDeck} />

      <main className="container mx-auto px-4 py-8 max-w-6xl">
        {isLoading && (
          <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
            <LoadingSpinner size="lg" />
          </div>
        )}

        {currentView === "home" && (
          <div className="space-y-8">
            <div className="text-center space-y-4">
              <h1 className="text-4xl font-bold text-foreground text-balance">
                Transform Your Notes Into Smart Flashcards
              </h1>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto text-pretty">
                Paste your study notes and let AI generate personalized flashcards to help you learn more effectively.
              </p>
            </div>

            <DeckList onStudyDeck={handleStudyDeck} onCreateDeck={handleCreateDeck} />
          </div>
        )}

        {currentView === "create" && <NoteInput onDeckCreated={handleDeckCreated} setIsLoading={setIsLoading} />}

        {currentView === "study" && selectedDeckId && (
          <FlashcardGrid deckId={selectedDeckId} onBackToDecks={handleBackToHome} />
        )}
      </main>
    </div>
  )
}
