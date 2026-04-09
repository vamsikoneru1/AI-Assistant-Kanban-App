# Project Plan

This document breaks the work into parts with checklists, tests, and success criteria. The user must review and approve Part 1 before any implementation starts.

## Part 1: Plan

Checklist
- [x] Enrich this plan with detailed substeps, tests, and success criteria per part.
- [x] Add frontend/AGENTS.md describing the existing frontend code.
- [x] Send the updated plan to the user for approval.
- [x] Do not start implementation until approval is received.

Tests
- [x] None (planning only).

Success criteria
- [x] The plan is detailed, test-focused, and approved by the user.
- [x] frontend/AGENTS.md exists and accurately describes current code.

## Part 2: Scaffolding

Checklist
- [x] Add Docker configuration for local containerized dev.
- [x] Create backend FastAPI app under backend/.
- [x] Serve a simple static HTML page at / from the backend.
- [x] Add a dummy API route (for example /api/health) and call it from the static page.
- [x] Add start/stop scripts for Mac, Windows, Linux under scripts/.

Tests
- [x] Manual smoke: run container, open / and confirm HTML renders.
- [x] Manual smoke: call the dummy API route and confirm response.

Success criteria
- [x] Container runs locally and serves HTML at /.
- [x] Dummy API responds with expected payload.
- [x] Start/stop scripts work on supported OS targets.

## Part 3: Add Frontend

Checklist
- [x] Update Docker and backend to serve the statically built frontend at /.
- [x] Wire build pipeline for frontend static assets.
- [x] Ensure the current Kanban demo loads at /.

Tests
- [x] Unit: existing frontend unit tests pass.
- [x] Integration: core Kanban interactions (rename, add, move, delete) covered.
- [x] Manual smoke: load / and verify UI renders.

Success criteria
- [x] Frontend static build is served by FastAPI at /.
- [x] Kanban demo is functional with existing interactions.

## Part 4: Fake User Sign-in

Checklist
- [x] Add login gate at / requiring "user" / "password".
- [x] Add logout control and session clearing.
- [x] Preserve the Kanban view after successful login.

Tests
- [x] Unit: login form validation and auth state transitions.
- [x] Integration: unauthenticated access redirects or blocks.
- [x] E2E: login and logout flow.

Success criteria
- [x] Only authenticated users can access the Kanban.
- [x] Login and logout behave consistently.

## Part 5: Database Modeling

Checklist
- [x] Propose a SQLite schema for users, boards, columns, cards.
- [x] Save schema JSON to docs/kanban-schema.json.
- [x] Add a brief design note under docs/ describing the approach.
- [x] Get user sign off before implementation.

Tests
- [x] None (modeling only).

Success criteria
- [x] Schema JSON and documentation exist in docs/.
- [x] User approves the schema.

## Part 6: Backend

Checklist
- [x] Create database on startup if missing.
- [x] Add CRUD routes for board, columns, cards per user.
- [x] Enforce single board per user.
- [x] Seed or bootstrap default board if none exists.

Tests
- [x] Unit: database layer CRUD.
- [x] Unit: API route behavior and validation.
- [x] Integration: end-to-end board read/write through API.

Success criteria
- [x] Backend persists and returns Kanban data per user.
- [x] Database auto-creates and survives restarts.

## Part 7: Frontend + Backend

Checklist
- [x] Replace local in-memory board with API-backed data.
- [x] Handle loading, error, and empty states.
- [x] Keep existing interactions (rename, add, move, delete).

Tests
- [x] Unit: API client helpers.
- [x] Integration: Kanban UI + API interactions.
- [x] E2E: full user flow with persistence.

Success criteria
- [x] Kanban changes persist across reloads.
- [x] UI stays responsive during API calls.

## Part 8: AI Connectivity

Checklist
- [x] Configure OpenRouter client in backend.
- [x] Add a simple backend route to call the model with "2+2".
- [x] Validate API key use from .env.

Tests
- [x] Unit: OpenRouter client wrapper.
- [x] Manual smoke: verify "2+2" returns "4" or equivalent.

Success criteria
- [x] AI calls succeed reliably through OpenRouter.

## Part 9: AI Structured Outputs

Checklist
- [x] Define structured output schema for AI responses.
- [x] Send board JSON + user prompt + conversation history to AI.
- [x] Parse structured output, apply optional board updates.

Tests
- [x] Unit: schema validation and parsing.
- [x] Integration: AI route with mocked response.
- [x] Manual smoke: verify board update path.

Success criteria
- [x] AI responses are validated and applied safely.
- [x] User-facing response is consistent and reliable.

## Part 10: AI Chat UI

Checklist
- [x] Add sidebar chat UI.
- [ ] Stream or poll for AI responses.
- [x] Apply AI-driven board updates and refresh UI.
- [x] Preserve conversation history per user session.

Tests
- [x] Unit: chat state reducer or store.
- [x] Integration: chat sends, receives, and updates board.
- [ ] E2E: full chat-driven update flow.

Success criteria
- [x] Chat UI feels integrated and stable.
- [x] AI-driven updates are reflected immediately in the Kanban.