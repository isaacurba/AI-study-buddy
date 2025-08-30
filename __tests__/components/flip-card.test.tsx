import { render, screen, fireEvent } from "@testing-library/react"
import { FlipCard } from "@/components/ui/flip-card"
import jest from "jest" // Import jest to fix the undeclared variable error

describe("FlipCard", () => {
  const mockProps = {
    question: "What is the capital of France?",
    answer: "Paris is the capital of France.",
    difficulty: "easy" as const,
    isFlipped: false,
    onFlip: jest.fn(),
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it("renders question when not flipped", () => {
    render(<FlipCard {...mockProps} />)

    expect(screen.getByText("What is the capital of France?")).toBeInTheDocument()
    expect(screen.getByText("Question")).toBeInTheDocument()
    expect(screen.getByText("Click to reveal answer")).toBeInTheDocument()
  })

  it("renders answer when flipped", () => {
    render(<FlipCard {...mockProps} isFlipped={true} />)

    expect(screen.getByText("Paris is the capital of France.")).toBeInTheDocument()
    expect(screen.getByText("Answer")).toBeInTheDocument()
    expect(screen.getByText("Click to show question")).toBeInTheDocument()
  })

  it("displays correct difficulty badge", () => {
    render(<FlipCard {...mockProps} />)

    expect(screen.getByText("easy")).toBeInTheDocument()
  })

  it("calls onFlip when clicked", () => {
    render(<FlipCard {...mockProps} />)

    const card = screen.getByText("What is the capital of France?").closest(".flip-card-front")
    fireEvent.click(card!)

    expect(mockProps.onFlip).toHaveBeenCalledTimes(1)
  })

  it("applies correct CSS classes for difficulty levels", () => {
    const { rerender } = render(<FlipCard {...mockProps} difficulty="easy" />)
    expect(screen.getByText("easy")).toHaveClass("bg-emerald-100", "text-emerald-800")

    rerender(<FlipCard {...mockProps} difficulty="medium" />)
    expect(screen.getByText("medium")).toHaveClass("bg-amber-100", "text-amber-800")

    rerender(<FlipCard {...mockProps} difficulty="hard" />)
    expect(screen.getByText("hard")).toHaveClass("bg-red-100", "text-red-800")
  })

  it("has proper accessibility attributes", () => {
    render(<FlipCard {...mockProps} />)

    const questionCard = screen.getByText("What is the capital of France?").closest(".flip-card-front")
    expect(questionCard).toHaveClass("cursor-pointer")
  })
})
