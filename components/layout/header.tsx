"use client"

import { Button } from "@/components/ui/button"
import { ArrowLeft, Plus, BookOpen } from "lucide-react"

interface HeaderProps {
  currentView: "home" | "create" | "study"
  onBackToHome: () => void
  onCreateDeck: () => void
}

export function Header({ currentView, onBackToHome, onCreateDeck }: HeaderProps) {
  return (
    <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-40">
      <div className="container mx-auto px-4 py-4 max-w-6xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {currentView !== "home" && (
              <Button variant="ghost" size="sm" onClick={onBackToHome} className="gap-2">
                <ArrowLeft className="h-4 w-4" />
                Back
              </Button>
            )}

            <div className="flex items-center gap-2">
              <BookOpen className="h-6 w-6 text-primary" />
              <h1 className="text-xl font-bold text-foreground">AI Study Buddy</h1>
            </div>
          </div>

          {currentView === "home" && (
            <Button onClick={onCreateDeck} className="gap-2">
              <Plus className="h-4 w-4" />
              Create New Deck
            </Button>
          )}
        </div>
      </div>
    </header>
  )
}
