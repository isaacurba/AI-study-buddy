import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { DeckList } from "@/components/deck-list"
import jest from "jest" // Import jest to declare the variable

// Mock the toast hook
jest.mock("@/hooks/use-toast", () => ({
  useToast: () => ({
    toast: jest.fn(),
  }),
}))

describe("DeckList", () => {
  const mockProps = {
    onStudyDeck: jest.fn(),
    onCreateDeck: jest.fn(),
  }

  beforeEach(() => {
    jest.clearAllMocks()
    global.fetch = jest.fn()
  })

  it("shows loading spinner initially", () => {
    render(<DeckList {...mockProps} />)
    expect(screen.getByTestId("loading-spinner")).toBeInTheDocument()
  })

  it("shows empty state when no decks exist", async () => {
    const mockFetch = global.fetch as jest.Mock
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ decks: [] }),
    })

    render(<DeckList {...mockProps} />)

    await waitFor(() => {
      expect(screen.getByText(/no flashcard decks yet/i)).toBeInTheDocument()
    })

    expect(screen.getByRole("button", { name: /create your first deck/i })).toBeInTheDocument()
  })

  it("displays decks when they exist", async () => {
    const mockDecks = [
      {
        id: 1,
        title: "Biology Chapter 1",
        description: "Cell structure",
        flashcard_count: 5,
        created_at: "2024-01-15T10:30:00Z",
      },
    ]

    const mockFetch = global.fetch as jest.Mock
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ decks: mockDecks }),
    })

    render(<DeckList {...mockProps} />)

    await waitFor(() => {
      expect(screen.getByText("Biology Chapter 1")).toBeInTheDocument()
    })

    expect(screen.getByText("Cell structure")).toBeInTheDocument()
    expect(screen.getByText("5 cards")).toBeInTheDocument()
  })

  it("calls onStudyDeck when Study Deck button is clicked", async () => {
    const user = userEvent.setup()
    const mockDecks = [
      {
        id: 1,
        title: "Biology Chapter 1",
        description: "Cell structure",
        flashcard_count: 5,
        created_at: "2024-01-15T10:30:00Z",
      },
    ]

    const mockFetch = global.fetch as jest.Mock
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ decks: mockDecks }),
    })

    render(<DeckList {...mockProps} />)

    await waitFor(() => {
      expect(screen.getByText("Biology Chapter 1")).toBeInTheDocument()
    })

    const studyButton = screen.getByRole("button", { name: /study deck/i })
    await user.click(studyButton)

    expect(mockProps.onStudyDeck).toHaveBeenCalledWith(1)
  })

  it("calls onCreateDeck when Create New Deck button is clicked", async () => {
    const user = userEvent.setup()
    const mockFetch = global.fetch as jest.Mock
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ decks: [] }),
    })

    render(<DeckList {...mockProps} />)

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /create your first deck/i })).toBeInTheDocument()
    })

    const createButton = screen.getByRole("button", { name: /create your first deck/i })
    await user.click(createButton)

    expect(mockProps.onCreateDeck).toHaveBeenCalled()
  })
})
