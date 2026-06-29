# D7: The Co-pilot Shell (Agentic Prompting Artifact)

## Overview
The Co-pilot Shell is a localhost-deployable full-stack application that wraps the 4-stage
prompt pipeline in an interactive support-agent interface. It demonstrates the pipeline in a
realistic, usable form: an agent (or reviewer) pastes a customer ticket and receives a
policy-grounded draft reply.

The shell is intentionally a **thin wrapper** — all intelligence lives in the prompts
(`prompts/`) and the pipeline (`src/pipeline.py`). The app contains no policy logic of its own.

---

## Architecture

Browser (React chat widget) FastAPI backend 4-stage pipeline localhost:5173 ──HTTP──▶ localhost:8000 ──call──▶ src/pipeline.py │ ▼ OpenAI-compatible LLM client (Gemini via base_url)


- **Frontend** (`frontend/`): React + Vite floating chat widget (Sobot-style bubble).
- **Backend** (`backend/`): FastAPI exposing the pipeline over REST.
- **Pipeline** (`src/`): the 4 stages + LLM client abstraction (unchanged by the shell).
- **Separation of concerns:** frontend handles UI only; backend handles HTTP only; the
  pipeline handles all reasoning.

---

## Frontend (React + Vite)
A componentized floating chat widget:

|      Component      |                              Responsibility                                |
|---------------------|----------------------------------------------------------------------------|
| `App.jsx`           | State manager (open/closed, messages, loading, online status) + send logic |
| `ChatButton.jsx`    | Floating circular launcher button                                          |
| `ChatWidget.jsx`    | Panel container (vertical flexbox: header / messages / input)              |
| `ChatHeader.jsx`    | Title, online/offline status dot, close button                             |
| `MessageList.jsx`   | Scrollable messages, auto-scroll, typing indicator, starter questions      |
| `MessageBubble.jsx` | Single message (user right / bot left) + behavior badge                    |
| `ChatInput.jsx`     | Textarea + send button (Enter to send)                                     |
| `api.js`            | All backend calls (`getHealth`, `getTickets`, `sendTicket`)                |


Each component has its own co-located CSS file for maintainability.

---

## Backend (FastAPI)
Endpoints (prefixed `/api`):

|    Endpoint        | Method |                    Purpose                          |
|--------------------|--------|-----------------------------------------------------|
| `/api/health`      |  GET   | Backend + LLM-client status (drives the online dot) |
| `/api/policy`      |  GET   | Returns policy passages [P1]–[P8]                   |
| `/api/tickets`     |  GET   | Returns the 14 test tickets                         |
| `/api/ticket`      |  POST  | Runs the full 4-stage pipeline on a custom ticket   |
| `/api/ticket/{id}` |  POST  | Runs the pipeline on a test-set ticket by ID        |

The backend imports and calls `src/pipeline.py` directly — it never duplicates pipeline logic.
`.env` is loaded at startup so the LLM client (Gemini) is configured before any request.

---

## LLM Client Abstraction
A single `OpenAIClient` (in `src/llm_client.py`) targets any OpenAI-compatible endpoint via a
configurable `base_url`:

| Provider       |                  OPENAI_BASE_URL                           |  Notes    |
|----------------|------------------------------------------------------------|-----------|
| Gemini (used)  | `https://generativelanguage.googleapis.com/v1beta/openai/` | Free tier |

This abstraction means the model can be swapped via `.env` alone — no code changes.

---

## How to Run Locally

**Backend** (terminal 1):
uvicorn backend.main:app --reload --reload-dir backend --reload-dir src --port 8000


**Frontend** (terminal 2):
cd frontend npm install npm run dev # opens http://localhost:5173


**Configuration** (`.env` at project root):
GEMINI_API_KEY= OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/ OPENAI_MODEL=gemini-2.5-flash


A VS Code task ("Start All") and/or `concurrently` script can launch both servers with one
command.

---

## Agentic Prompting Notes (how the shell was built)
The shell itself was constructed iteratively with AI coding assistants (GitHub Copilot /
Cursor-style agents). Key directives given to the agent included:
- "Build a FastAPI wrapper that IMPORTS and calls `src/pipeline.py` — do not duplicate the
  pipeline logic."
- "Make the frontend a componentized floating chat widget; keep all backend calls in `api.js`."
- "Load `.env` before importing modules that read environment variables."
- "Treat the prompts in `prompts/` as the single source of truth."

This kept the generated code aligned with the architecture (thin shell, prompts as the
deliverable) rather than letting the agent re-implement business logic.

---

## Screenshot
[Insert a screenshot of the chat widget here — the floating bubble open, showing a
ticket and its grounded reply.]

---

## Design Principle
**The app is disposable; the prompts are the deliverable.** The shell exists to demonstrate
and exercise the pipeline, not to contain intelligence. All policy reasoning, grounding, and
guardrails live in the prompts and pipeline — the UI simply sends a ticket and displays the
result.