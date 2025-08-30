"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface FlipCardProps {
  question: string
  answer: string
  difficulty: "easy" | "medium" | "hard"
  isFlipped: boolean
  onFlip: () => void
  className?: string
}

export function FlipCard({ question, answer, difficulty, isFlipped, onFlip, className }: FlipCardProps) {
  const [isAnimating, setIsAnimating] = useState(false)

  const getDifficultyColor = (level: string) => {
    switch (level) {
      case "easy":
        return "bg-emerald-100 text-emerald-800 border-emerald-200 dark:bg-emerald-900/20 dark:text-emerald-400 dark:border-emerald-800"
      case "medium":
        return "bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-900/20 dark:text-amber-400 dark:border-amber-800"
      case "hard":
        return "bg-red-100 text-red-800 border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  const handleClick = () => {
    if (isAnimating) return

    setIsAnimating(true)
    onFlip()

    // Reset animation state after flip completes
    setTimeout(() => {
      setIsAnimating(false)
    }, 600)
  }

  return (
    <div className={cn("flip-card min-h-[400px]", isFlipped && "flipped", className)}>
      <div className="flip-card-inner">
        {/* Front of card - Question */}
        <Card className="flip-card-front bg-card border-border cursor-pointer" onClick={handleClick}>
          <CardContent className="p-8 h-full flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <Badge variant="outline" className={getDifficultyColor(difficulty)}>
                {difficulty}
              </Badge>
              <span className="text-sm text-muted-foreground">Click to reveal answer</span>
            </div>

            <div className="flex-1 flex flex-col justify-center space-y-6">
              <div className="text-center space-y-4">
                <h3 className="text-lg font-medium text-primary uppercase tracking-wide">Question</h3>
                <p className="text-xl leading-relaxed text-foreground text-balance">{question}</p>
              </div>
            </div>

            <div className="text-center">
              <div className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary">
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l4-4 4 4m0 6l-4 4-4-4" />
                </svg>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Back of card - Answer */}
        <Card className="flip-card-back bg-primary/5 border-primary/20 cursor-pointer" onClick={handleClick}>
          <CardContent className="p-8 h-full flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <Badge variant="outline" className={getDifficultyColor(difficulty)}>
                {difficulty}
              </Badge>
              <span className="text-sm text-muted-foreground">Click to show question</span>
            </div>

            <div className="flex-1 flex flex-col justify-center space-y-6">
              <div className="text-center space-y-4">
                <h3 className="text-lg font-medium text-primary uppercase tracking-wide">Answer</h3>
                <p className="text-xl leading-relaxed text-foreground text-pretty">{answer}</p>
              </div>
            </div>

            <div className="text-center">
              <div className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary">
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
