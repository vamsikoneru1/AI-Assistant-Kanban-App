"use client";

import { useEffect, useMemo, useState } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";

const AUTH_KEY = "pm-auth";
const VALID_USER = "user";
const VALID_PASSWORD = "password";

export const LoginGate = () => {
  const [isReady, setIsReady] = useState(false);
  const [isAuthed, setIsAuthed] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const stored = window.localStorage.getItem(AUTH_KEY);
    setIsAuthed(stored === "true");
    setIsReady(true);
  }, []);

  const canSubmit = useMemo(
    () => username.trim().length > 0 && password.trim().length > 0,
    [username, password]
  );

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const isValid = username === VALID_USER && password === VALID_PASSWORD;
    if (!isValid) {
      setError("Invalid credentials. Use user / password.");
      return;
    }
    window.localStorage.setItem(AUTH_KEY, "true");
    setIsAuthed(true);
    setError("");
  };

  const handleLogout = () => {
    window.localStorage.removeItem(AUTH_KEY);
    setIsAuthed(false);
    setUsername("");
    setPassword("");
  };

  if (!isReady) {
    return null;
  }

  if (!isAuthed) {
    return (
      <main className="mx-auto flex min-h-screen max-w-4xl flex-col items-center justify-center px-6 py-12">
        <div className="w-full max-w-md rounded-[28px] border border-[var(--stroke)] bg-white/90 p-8 shadow-[var(--shadow)]">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-[var(--gray-text)]">
            Sign in
          </p>
          <h1 className="mt-3 font-display text-3xl font-semibold text-[var(--navy-dark)]">
            Welcome back
          </h1>
          <p className="mt-2 text-sm leading-6 text-[var(--gray-text)]">
            Use the demo credentials to access your Kanban board.
          </p>
          <form className="mt-6 flex flex-col gap-4" onSubmit={handleSubmit}>
            <label className="flex flex-col gap-2 text-sm font-semibold text-[var(--navy-dark)]">
              Username
              <input
                className="rounded-xl border border-[var(--stroke)] bg-white px-3 py-2 text-sm outline-none focus:border-[var(--primary-blue)]"
                type="text"
                autoComplete="username"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
              />
            </label>
            <label className="flex flex-col gap-2 text-sm font-semibold text-[var(--navy-dark)]">
              Password
              <input
                className="rounded-xl border border-[var(--stroke)] bg-white px-3 py-2 text-sm outline-none focus:border-[var(--primary-blue)]"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </label>
            {error ? (
              <p className="text-sm font-semibold text-[var(--secondary-purple)]">
                {error}
              </p>
            ) : null}
            <button
              type="submit"
              className="rounded-full bg-[var(--secondary-purple)] px-4 py-2 text-sm font-semibold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
              disabled={!canSubmit}
            >
              Sign in
            </button>
          </form>
          <div className="mt-6 rounded-2xl border border-dashed border-[var(--stroke)] px-4 py-3 text-xs text-[var(--gray-text)]">
            Demo credentials: <strong>user</strong> / <strong>password</strong>
          </div>
        </div>
      </main>
    );
  }

  return (
    <div className="relative">
      <div className="pointer-events-none absolute left-0 top-0 h-[260px] w-[260px] -translate-x-1/3 -translate-y-1/3 rounded-full bg-[radial-gradient(circle,_rgba(236,173,10,0.25)_0%,_rgba(236,173,10,0.06)_55%,_transparent_70%)]" />
      <div className="absolute right-6 top-6 z-10 flex items-center gap-3 rounded-full border border-[var(--stroke)] bg-white/80 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--navy-dark)] backdrop-blur">
        <span className="h-2 w-2 rounded-full bg-[var(--accent-yellow)]" />
        Signed in
        <button
          type="button"
          onClick={handleLogout}
          className="rounded-full border border-transparent px-2 py-1 text-xs font-semibold text-[var(--gray-text)] transition hover:border-[var(--stroke)] hover:text-[var(--navy-dark)]"
        >
          Log out
        </button>
      </div>
      <KanbanBoard />
    </div>
  );
};
