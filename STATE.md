# State & Global Memory

**Librarian**: Agent-Librarian (Model: gemini-3-flash)
**Last Updated**: 2026-02-08 15:05

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We are in the **Polishing & Verification** phase — refining UI/UX and ensuring system stability.

## 🔄 Recent Changes (2026-02-19 Agent Handoffs)
- **Workflow Standardization**: Created a standardized Agent Handoff protocol across all `roles/*.md` to explicitly format expectations.
- **Context Preservation**: Added `Status Summary` and `Artifacts` links to handoff prompts to mitigate position bias between role shifts.

## 📍 System State
- **Backend**: Port 8000. Coverage >80% (Notifications added).
- **Frontend**: Port 5173. Notifications enabled. Sidebar resizable.
- **Tests**: All backend tests passed. Browser verification success.

## 🚧 Active Tasks
1. **Gamification Polish**: Review point/reward scaling (Next).
2. **Task Import/Export UI**: Finalize modal design based on `import_wizard` logic.

## ⚠️ Known Issues / Watchlist
- **Migration Edge Cases**: `SQLAlchemy` auto-migrations are limited; use `alembic` for complex schema changes.
- **Timezone**: "Europe/Berlin" set in config but relies on system time in some Docker contexts.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — Agent Handoffs are complete. Let's proceed with **Gamification Polish**."
