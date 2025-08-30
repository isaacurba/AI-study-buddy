"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Sparkles, FileText } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface NoteInputProps {
  onDeckCreated: () => void
  setIsLoading: (loading: boolean) => void
}

export function NoteInput({ onDeckCreated, setIsLoading }: NoteInputProps) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [notes, setNotes] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)
  const { toast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!title.trim() || !notes.trim()) {
      toast({
        title: "Missing Information",
        description: "Please provide both a title and your study notes.",
        variant: "destructive",
      })
      return
    }

    if (notes.trim().length < 50) {
      toast({
        title: "Notes Too Short",
        description: "Please provide more detailed notes (at least 50 characters) for better flashcard generation.",
        variant: "destructive",
      })
      return
    }

    setIsGenerating(true)
    setIsLoading(true)

    try {
      // Simulate API call to backend
      const response = await fetch("/api/decks", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: title.trim(),
          description: description.trim(),
          notes: notes.trim(),
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to create deck")
      }

      const result = await response.json()

      toast({
        title: "Deck Created Successfully!",
        description: `Generated ${result.flashcard_count} flashcards from your notes.`,
      })

      // Reset form
      setTitle("")
      setDescription("")
      setNotes("")

      onDeckCreated()
    } catch (error) {
      console.error("Error creating deck:", error)
      toast({
        title: "Creation Failed",
        description: "There was an error creating your flashcard deck. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsGenerating(false)
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-bold text-foreground">Create New Flashcard Deck</h2>
        <p className="text-muted-foreground">
          Paste your study notes below and AI will generate personalized flashcards for you.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            Deck Information
          </CardTitle>
          <CardDescription>Give your flashcard deck a title and optional description.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="title">Deck Title *</Label>
                <Input
                  id="title"
                  placeholder="e.g., Biology Chapter 5: Cell Structure"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description (Optional)</Label>
                <Input
                  id="description"
                  placeholder="Brief description of the topic"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Study Notes *</Label>
              <Textarea
                id="notes"
                placeholder="Paste your study notes here... The more detailed your notes, the better the AI can generate relevant flashcards. Include definitions, key concepts, processes, and important facts."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="min-h-[300px] resize-y"
                required
              />
              <p className="text-sm text-muted-foreground">
                {notes.length} characters • Minimum 50 characters recommended
              </p>
            </div>

            <div className="flex justify-end gap-3">
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setTitle("")
                  setDescription("")
                  setNotes("")
                }}
                disabled={isGenerating}
              >
                Clear All
              </Button>
              <Button type="submit" disabled={isGenerating || !title.trim() || !notes.trim()} className="gap-2">
                {isGenerating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary-foreground border-t-transparent" />
                    Generating Flashcards...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4" />
                    Generate Flashcards
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card className="bg-muted/50">
        <CardContent className="pt-6">
          <div className="space-y-3">
            <h3 className="font-semibold text-foreground">Tips for Better Flashcards:</h3>
            <ul className="space-y-1 text-sm text-muted-foreground">
              <li>• Include clear definitions and explanations</li>
              <li>• Add specific examples and key facts</li>
              <li>• Structure your notes with headings and bullet points</li>
              <li>• Include processes, steps, and cause-effect relationships</li>
              <li>• The AI will generate 5 flashcards from your notes</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
