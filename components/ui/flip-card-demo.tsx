"use client"

import { useState } from "react"
import { FlipCard } from "./flip-card"
import { Button } from "./button"

export function FlipCardDemo() {
  const [isFlipped, setIsFlipped] = useState(false)

  return (
    <div className="max-w-md mx-auto space-y-4">
      <FlipCard
        question="What is the capital of France?"
        answer="Paris is the capital and most populous city of France, known for its art, fashion, gastronomy, and culture."
        difficulty="easy"
        isFlipped={isFlipped}
        onFlip={() => setIsFlipped(!isFlipped)}
      />

      <div className="text-center">
        <Button onClick={() => setIsFlipped(!isFlipped)}>{isFlipped ? "Show Question" : "Show Answer"}</Button>
      </div>
    </div>
  )
}
