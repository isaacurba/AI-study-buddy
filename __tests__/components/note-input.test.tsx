import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { NoteInput } from "@/components/note-input"
import jest from "jest"

// Mock the toast hook
jest.mock("@/hooks/use-toast", () => ({
  useToast: () => ({
    toast: jest.fn(),
  }),
}))

describe("NoteInput", () => {
  const mockProps = {
    onDeckCreated: jest.fn(),
    setIsLoading: jest.fn(),
  }

  beforeEach(() => {
    jest.clearAllMocks()
    global.fetch = jest.fn()
  })

  it("renders form elements correctly", () => {
    render(<NoteInput {...mockProps} />)

    expect(screen.getByLabelText(/deck title/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/study notes/i)).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /generate flashcards/i })).toBeInTheDocument()
  })

  it("shows character count for notes", async () => {
    const user = userEvent.setup()
    render(<NoteInput {...mockProps} />)

    const notesTextarea = screen.getByLabelText(/study notes/i)
    await user.type(notesTextarea, "Test notes")

    expect(screen.getByText(/10 characters/i)).toBeInTheDocument()
  })

  it("disables submit button when form is invalid", () => {
    render(<NoteInput {...mockProps} />)

    const submitButton = screen.getByRole("button", { name: /generate flashcards/i })
    expect(submitButton).toBeDisabled()
  })

  it("enables submit button when form is valid", async () => {
    const user = userEvent.setup()
    render(<NoteInput {...mockProps} />)

    await user.type(screen.getByLabelText(/deck title/i), "Test Deck")
    await user.type(
      screen.getByLabelText(/study notes/i),
      "This is a test note with enough characters to meet the minimum requirement.",
    )

    const submitButton = screen.getByRole("button", { name: /generate flashcards/i })
    expect(submitButton).toBeEnabled()
  })

  it("clears form when Clear All is clicked", async () => {
    const user = userEvent.setup()
    render(<NoteInput {...mockProps} />)

    const titleInput = screen.getByLabelText(/deck title/i)
    const notesTextarea = screen.getByLabelText(/study notes/i)

    await user.type(titleInput, "Test Title")
    await user.type(notesTextarea, "Test notes")

    const clearButton = screen.getByRole("button", { name: /clear all/i })
    await user.click(clearButton)

    expect(titleInput).toHaveValue("")
    expect(notesTextarea).toHaveValue("")
  })

  it("submits form with correct data", async () => {
    const user = userEvent.setup()
    const mockFetch = global.fetch as jest.Mock
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ flashcard_count: 5 }),
    })

    render(<NoteInput {...mockProps} />)

    await user.type(screen.getByLabelText(/deck title/i), "Biology Chapter 1")
    await user.type(screen.getByLabelText(/description/i), "Cell structure")
    await user.type(
      screen.getByLabelText(/study notes/i),
      "Cells are the basic unit of life. They contain organelles like mitochondria.",
    )

    const submitButton = screen.getByRole("button", { name: /generate flashcards/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith("/api/decks", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: "Biology Chapter 1",
          description: "Cell structure",
          notes: "Cells are the basic unit of life. They contain organelles like mitochondria.",
        }),
      })
    })

    expect(mockProps.onDeckCreated).toHaveBeenCalled()
  })
})
