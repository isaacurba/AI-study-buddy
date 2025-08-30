"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Play, Plus, Trash2, Calendar } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { LoadingSpinner } from "@/components/ui/loading-spinner"

interface Deck {
  id: number
  title: string
  description: string
  flashcard_count: number
  created_at: string
}

interface DeckListProps {
  onStudyDeck: (deckId: number) => void
  onCreateDeck: () => void
}

export function DeckList({ onStudyDeck, onCreateDeck }: DeckListProps) {
  const [decks, setDecks] = useState<Deck[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const { toast } = useToast()

  useEffect(() => {
    fetchDecks()
  }, [])

  const fetchDecks = async () => {
    try {
      // Simulate API call - replace with actual backend call
      const response = await fetch("/api/decks")
      if (response.ok) {
        const data = await response.json()
        setDecks(data.decks || [])
      } else {
        // For demo purposes, show sample data
        setDecks([
          {
            id: 1,
            title: "Biology Chapter 5: Cell Structure",
            description: "Organelles, membranes, and cellular processes",
            flashcard_count: 8,
            created_at: "2024-01-15T10:30:00Z",
          },
          {
            id: 2,
            title: "World History: Renaissance Period",
            description: "Key figures, events, and cultural changes",
            flashcard_count: 12,
            created_at: "2024-01-14T14:20:00Z",
          },
          {
            id: 3,
            title: "Chemistry: Atomic Structure",
            description: "Electrons, protons, neutrons, and periodic trends",
            flashcard_count: 6,
            created_at: "2024-01-13T09:15:00Z",
          },
        ])
      }
    } catch (error) {
      console.error("Error fetching decks:", error)
      toast({
        title: "Error Loading Decks",
        description: "Unable to load your flashcard decks. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteDeck = async (deckId: number, deckTitle: string) => {
    if (!confirm(`Are you sure you want to delete "${deckTitle}"? This action cannot be undone.`)) {
      return
    }

    setDeletingId(deckId)

    try {
      const response = await fetch(`/api/decks/${deckId}`, {
        method: "DELETE",
      })

      if (response.ok) {
        setDecks(decks.filter((deck) => deck.id !== deckId))
        toast({
          title: "Deck Deleted",
          description: `"${deckTitle}" has been deleted successfully.`,
        })
      } else {
        throw new Error("Failed to delete deck")
      }
    } catch (error) {
      console.error("Error deleting deck:", error)
      toast({
        title: "Delete Failed",
        description: "Unable to delete the deck. Please try again.",
        variant: "destructive",
      })
    } finally {
      setDeletingId(null)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    })
  }

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (decks.length === 0) {
    return (
      <Card className="text-center py-12">
        <CardContent>
          <div className="space-y-4">
            <div className="mx-auto w-16 h-16 bg-muted rounded-full flex items-center justify-center">
              <Plus className="h-8 w-8 text-muted-foreground" />
            </div>
            <div className="space-y-2">
              <h3 className="text-xl font-semibold text-foreground">No Flashcard Decks Yet</h3>
              <p className="text-muted-foreground max-w-md mx-auto">
                Create your first flashcard deck by pasting your study notes and letting AI generate personalized
                questions for you.
              </p>
            </div>
            <Button onClick={onCreateDeck} className="gap-2">
              <Plus className="h-4 w-4" />
              Create Your First Deck
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Your Flashcard Decks</h2>
          <p className="text-muted-foreground">
            {decks.length} deck{decks.length !== 1 ? "s" : ""} ready for study
          </p>
        </div>
        <Button onClick={onCreateDeck} className="gap-2">
          <Plus className="h-4 w-4" />
          Create New Deck
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {decks.map((deck) => (
          <Card key={deck.id} className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <CardTitle className="text-lg leading-tight text-balance">{deck.title}</CardTitle>
                  {deck.description && (
                    <CardDescription className="mt-1 text-pretty">{deck.description}</CardDescription>
                  )}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDeleteDeck(deck.id, deck.title)}
                  disabled={deletingId === deck.id}
                  className="text-muted-foreground hover:text-destructive shrink-0"
                >
                  {deletingId === deck.id ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent" />
                  ) : (
                    <Trash2 className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Calendar className="h-4 w-4" />
                  {formatDate(deck.created_at)}
                </div>
                <Badge variant="secondary">{deck.flashcard_count} cards</Badge>
              </div>

              <Button onClick={() => onStudyDeck(deck.id)} className="w-full gap-2">
                <Play className="h-4 w-4" />
                Study Deck
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
