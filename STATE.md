# State & Global Memory

**Librarian**: Agent-Librarian (Model: gemini-3-flash)
**Last Updated**: 2026-02-08 15:05

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We are in the **Polishing & Verification** phase — refining UI/UX and ensuring system stability.

## 🔄 Recent Changes (2026-02-20 Reward Hub UI Polish)
- **Gamification**: Added `current_streak` and `last_task_date` to `User` model. Implemented +5 point daily bonus and streak multipliers (up to +0.5).
- **Reward Hub Polish**: Implemented a tiered layout (Bronze, Silver, Gold), premium Glassmorphism aesthetics, a pulsing affordable design, and a real-time math breakdown in the redemption confirmation modal. Added missing i18n EN/DE keys.

## 📍 System State
- **Backend**: Port 8000. Coverage >80%.
- **Frontend**: Port 5173. Reward Hub UI Polish verified. All linting/typechecks passing.
- **Tests**: All backend tests passed. Browser verification success.

## 🚧 Active Tasks
1. **Task Import/Export UI**: Finalize modal design based on `import_wizard` logic (Next).

## ⚠️ Known Issues / Watchlist
- **Migration Edge Cases**: `SQLAlchemy` auto-migrations are limited; use `alembic` for complex schema changes.
- **Timezone**: "Europe/Berlin" set in config but relies on system time in some Docker contexts.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — Reward Hub UI Polish is complete. Let's proceed with **Task Import/Export UI**."
