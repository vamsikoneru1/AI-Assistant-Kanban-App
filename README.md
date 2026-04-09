# Kanban AI Assistant MVP

A local-first Project Management MVP with a Next.js frontend, a FastAPI backend, and an AI assistant via OpenRouter. The app runs in a single Docker container and uses SQLite for persistence.

## Features

- Kanban board with drag-and-drop, rename, add, and delete
- Login gate (demo credentials: user / password)
- SQLite persistence with a single board per user (MVP)
- AI chat sidebar powered by OpenRouter

## Requirements

- Docker Desktop
- Node.js 20+ (only for local frontend tests)
- Python 3.9+ (only for local backend tests)

## Quick Start

```bash
./scripts/start.sh
```

Open http://localhost:8000

Stop the container:

```bash
./scripts/stop.sh
```

Windows PowerShell:

```powershell
./scripts/start.ps1
./scripts/stop.ps1
```

## Environment

Create backend/.env with the following:

```
OPENROUTER_API_KEY=your_key_here
```

## Tests

Frontend unit tests:

```bash
cd frontend
npm install
npm run test:unit
```

Frontend E2E tests:

```bash
cd frontend
npm run test:e2e
```

Backend tests:

```bash
cd backend
python3 -m pip install -r requirements.txt
python3 -m pytest
```

## Project Structure

- frontend/ Next.js app (static export)
- backend/ FastAPI API + SQLite
- scripts/ Start/stop scripts for Docker
- docs/ Planning and design docs

## Notes

- SQLite data is persisted to backend/data/pm.db via a Docker volume.
- The AI endpoint used by the UI is POST /api/ai/structured.
