# State & Global Memory

**Librarian**: Agent-Librarian (Model: gemini-3-flash)
**Last Updated**: 2026-02-08 15:05

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We are in the **Polishing & Verification** phase — refining UI/UX and ensuring system stability.

## 🔄 Recent Changes (2026-02-08 Session 2)

### DB Versioning & Deployment Fix (v1.3)
- **Backend**:
  - `MigrationManager` added: Auto-versions DB on startup (v1.3)
  - Consolidated migration script: Idempotent column additions for tasks, transactions, and users
  - Enforced migrations via new `rules.json` constraint (`MIGRATION_REQUIRED`)
- **Frontend**:
  - **Error Handling**: Improved `TaskManagement` to show clear DB error UI with "Retry" button
  - **Linting**: Fixed `any` type issues and `useCallback` dependency warnings
- **Stability**: Confirmed schema consistency for Synology deployments

### Deployment & Stability
- Confirmed Backend runs on port **8000**
- Frontend SSE connection updated to match
- Validated with `npm run build` and generic backend restart

## 📍 System State
- **Backend**: Port 8000 (CORRECTED from 8001). Stable.
- **Frontend**: Port 5173. Connected.
- **Database**: Schema v1.3 (Auto-versioning enabled).

## 🚧 Active Tasks
1. **Compliance Reports**: Needs UI graphs.
2. **Automated Backups**: Implementation needed.

## ⚠️ Known Issues / Watchlist
- Double-check `datetime` imports in new files.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — Workflow indicates 'Compliance Reports' is next. Let's design the UI graphs for task completion stats."

*This field is updated by the Librarian at the end of each session to guide the next agent.*
