import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ChatSidebar } from "@/components/ChatSidebar";
import { initialData } from "@/lib/kanban";

const noop = () => {};

describe("ChatSidebar", () => {
  it("sends a message and renders AI response", async () => {
    render(<ChatSidebar board={initialData} onBoardUpdate={noop} />);

    await userEvent.type(
      screen.getByPlaceholderText(/ask for an update/i),
      "What is 2+2?"
    );
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(await screen.findByText(/ai response/i)).toBeInTheDocument();
  });
});
