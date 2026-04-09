import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LoginGate } from "@/components/LoginGate";

const setLocalStorage = (value: string | null) => {
  if (value === null) {
    window.localStorage.removeItem("pm-auth");
  } else {
    window.localStorage.setItem("pm-auth", value);
  }
};

describe("LoginGate", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("shows the login form when logged out", async () => {
    render(<LoginGate />);
    expect(await screen.findByText(/welcome back/i)).toBeInTheDocument();
  });

  it("logs in with valid credentials", async () => {
    render(<LoginGate />);
    await userEvent.type(screen.getByLabelText(/username/i), "user");
    await userEvent.type(screen.getByLabelText(/password/i), "password");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByText(/signed in/i)).toBeInTheDocument();
    expect(window.localStorage.getItem("pm-auth")).toBe("true");
  });

  it("shows an error for invalid credentials", async () => {
    render(<LoginGate />);
    await userEvent.type(screen.getByLabelText(/username/i), "wrong");
    await userEvent.type(screen.getByLabelText(/password/i), "creds");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(
      await screen.findByText(/invalid credentials/i)
    ).toBeInTheDocument();
  });

  it("logs out and clears auth state", async () => {
    setLocalStorage("true");
    render(<LoginGate />);
    await screen.findByText(/signed in/i);

    await userEvent.click(screen.getByRole("button", { name: /log out/i }));

    expect(await screen.findByText(/welcome back/i)).toBeInTheDocument();
    expect(window.localStorage.getItem("pm-auth")).toBeNull();
  });
});
