# Frontend Overview

## Purpose

This frontend is a standalone Next.js demo that renders a single Kanban board UI. It does not connect to a backend yet.

## Entry Points

- src/app/page.tsx renders the Kanban board.
- src/app/layout.tsx wraps the app layout and global styles.
- src/app/globals.css defines theme variables and base styles.

## Core Components

- KanbanBoard: owns board state, drag-and-drop wiring, and column/card actions.
- KanbanColumn: renders a column, rename flow, add card flow.
- KanbanCard: sortable card with delete action.
- KanbanCardPreview: drag overlay preview.
- NewCardForm: add-card UI.

## Data and Logic

- src/lib/kanban.ts defines types, initial seed data, and move logic.
- Local React state in KanbanBoard holds the board data in memory.

## Tests

- Unit tests live in src/components and src/lib.
- E2E tests live under tests/ and use Playwright.

## Tooling

- Next.js app router in src/app.
- Drag and drop uses @dnd-kit.
- Styling is Tailwind-driven via className usage and CSS variables.
