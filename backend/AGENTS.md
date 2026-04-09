# Backend Overview

## Purpose

This backend is a minimal FastAPI service that serves the static frontend and exposes a SQLite-backed Kanban API.

## Entry Points

- app/main.py defines the FastAPI application.
- app/db.py handles SQLite connections, schema initialization, and seeding.

## Routes

- GET / serves the statically exported frontend (mounted from backend/static).
- GET /api/health returns a JSON health response.
- GET /api/board returns the current board for a user.
- PUT /api/board replaces the board payload.
- POST /api/columns creates a column.
- PATCH /api/columns/{column_id} renames a column.
- DELETE /api/columns/{column_id} deletes a column and its cards.
- POST /api/cards creates a card.
- PATCH /api/cards/{card_id} updates a card.
- DELETE /api/cards/{card_id} deletes a card.
- POST /api/ai calls OpenRouter with a prompt.
- POST /api/ai/structured calls OpenRouter with board context and structured output.

## Dependencies

- fastapi for the web framework.
- uvicorn[standard] for the ASGI server.