"use client";

import { useMemo, useState } from "react";
import type { BoardData } from "@/lib/kanban";

const MAX_MESSAGES = 50;

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

type ChatSidebarProps = {
  board: BoardData;
  onBoardUpdate: (board: BoardData) => void;
};

const createId = () => `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

export const ChatSidebar = ({ board, onBoardUpdate }: ChatSidebarProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState("");

  const canSend = useMemo(
    () => input.trim().length > 0 && !isSending,
    [input, isSending]
  );

  const handleSend = async () => {
    const question = input.trim();
    if (!question || isSending) {
      return;
    }

    const nextMessages: ChatMessage[] = [
      ...messages,
      { id: createId(), role: "user", content: question },
    ];
    setMessages(nextMessages.slice(-MAX_MESSAGES));
    setInput("");
    setIsSending(true);
    setError("");

    try {
      const response = await fetch("/api/ai/structured", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          board,
          history: nextMessages.map((message) => ({
            role: message.role,
            content: message.content,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error("AI request failed");
      }

      const data = (await response.json()) as {
        message?: string;
        updated?: boolean;
        board?: BoardData;
      };

      const assistantMessage = data.message ?? "I could not generate a response.";
      setMessages((prev) => {
        const next: ChatMessage[] = [
          ...prev,
          { id: createId(), role: "assistant", content: assistantMessage },
        ];
        return next.slice(-MAX_MESSAGES);
      });

      if (data.board) {
        onBoardUpdate(data.board);
      }
    } catch {
      setError("Unable to reach the AI service.");
    } finally {
      setIsSending(false);
    }
  };

  return (
    <aside className="flex h-full flex-col rounded-[28px] border border-[var(--stroke)] bg-white/90 p-5 shadow-[var(--shadow)] backdrop-blur">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-[var(--gray-text)]">
            AI Assistant
          </p>
          <h2 className="mt-2 font-display text-2xl font-semibold text-[var(--navy-dark)]">
            Board chat
          </h2>
        </div>
        <span className="rounded-full border border-[var(--stroke)] px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-[var(--primary-blue)]">
          Beta
        </span>
      </div>

      <div className="mt-4 flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto pr-1">
        {messages.length === 0 ? (
          <div className="flex flex-1 items-center justify-center rounded-2xl border border-dashed border-[var(--stroke)] px-4 py-8 text-center text-xs font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]">
            Ask the AI to update your board
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={
                message.role === "user"
                  ? "self-end rounded-2xl bg-[var(--primary-blue)] px-3 py-2 text-sm text-white"
                  : "self-start rounded-2xl border border-[var(--stroke)] bg-white px-3 py-2 text-sm text-[var(--navy-dark)]"
              }
            >
              {message.content}
            </div>
          ))
        )}
      </div>

      {error ? (
        <p className="mt-3 text-xs font-semibold text-[var(--secondary-purple)]">
          {error}
        </p>
      ) : null}

      <div className="mt-4 flex flex-col gap-2">
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask for an update or insight..."
          rows={3}
          className="w-full resize-none rounded-2xl border border-[var(--stroke)] bg-white px-3 py-2 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
        />
        <button
          type="button"
          onClick={handleSend}
          disabled={!canSend}
          className="rounded-full bg-[var(--secondary-purple)] px-4 py-2 text-xs font-semibold uppercase tracking-wide text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSending ? "Sending..." : "Send"}
        </button>
      </div>
    </aside>
  );
};
