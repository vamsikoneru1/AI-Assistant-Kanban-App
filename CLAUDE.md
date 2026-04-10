# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A local-first Kanban board with an AI chat assistant. The frontend (Next.js static export) is served by the FastAPI backend inside a single Docker container. SQLite handles persistence.

- Demo credentials: `user` / `password` (hardcoded; one board per user for MVP)
- AI chat uses OpenRouter (`openai/gpt-oss-120b`) via `POST /api/ai/structured`
- `backend/.env` must contain `OPENROUTER_API_KEY=your_key_here`

## Commands

### Run (Docker)
```bash
./scripts/start.sh   # starts container at http://localhost:8000
./scripts/stop.sh
```

### Frontend
```bash
cd frontend
npm install
npm run dev          # local dev server (hits /api/* via next.config.ts proxy)
npm run build        # static export to frontend/out/
npm run lint
npm run test:unit    # vitest
npm run test:e2e     # playwright
```

### Backend
```bash
cd backend
python3 -m pip install -r requirements.txt
uvicorn app.main:app --reload --app-dir backend   # local dev
python3 -m pytest                                  # all backend tests
python3 -m pytest tests/test_api.py::test_name    # single test
```

## Architecture

### Request Flow
1. Browser loads static Next.js from FastAPI's `/` static mount (`backend/static/`)
2. API calls go to `FastAPI` routes (`/api/*`)
3. Board mutations hit SQLite via `backend/app/db.py`
4. AI chat sends full board JSON + history to OpenRouter; response may include an `updatedBoard` that replaces the DB state atomically via `db.replace_board`

### Key Files
- `backend/app/main.py` — all API routes; Pydantic models for request/response shapes
- `backend/app/db.py` — all SQLite access; `get_board_id_for_username` auto-creates user+board on first call; `replace_board` does a full delete+reinsert (positions stored as integers)
- `backend/app/openrouter.py` — thin wrapper around OpenRouter HTTP calls
- `frontend/src/lib/kanban.ts` — board types (`BoardData`, `Column`, `Card`), `moveCard` logic, seed data
- `frontend/src/components/KanbanBoard.tsx` — owns all board state; fetches from `/api/board` on mount, saves via `PUT /api/board`
- `frontend/src/components/ChatSidebar.tsx` — AI chat UI; posts to `/api/ai/structured` and calls `onBoardUpdate` with the returned board

### Board Data Shape
```ts
{ columns: [{ id, title, cardIds }], cards: { [id]: { id, title, details } } }
```
Column order and card order within columns is determined by `position` integers in SQLite.

### DB Path Resolution (`backend/app/db.py`)
1. `PM_DB_PATH` env var if set
2. `backend/data/pm.db` if `data/` dir exists (Docker volume mount)
3. `backend/app/pm.db` fallback

## Coding Standards

- No over-engineering, no extra features beyond what is asked
- No emojis anywhere
- Identify root cause before fixing — do not guess
- Keep README minimal

## Color Scheme (CSS variables)
- `--accent-yellow: #ecad0a`
- `--primary-blue: #209dd7`
- `--secondary-purple: #753991`
- `--navy-dark: #032147`
- `--gray-text: #888888`
