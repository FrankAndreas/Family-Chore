# State & Global Memory

**Librarian**: Agent-Librarian (Model: gemini-3-flash)
**Last Updated**: 2026-02-08 15:05

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We are in the **Polishing & Verification** phase — refining UI/UX and ensuring system stability.

## 🔄 Recent Changes (2026-02-19 Gamification Polish)
- **Gamification**: Added `current_streak` and `last_task_date` to `User` model. Implemented +5 point daily bonus and streak multipliers (up to +0.5).
- **Frontend Badges**: Added visual indicators for daily bonuses and active streaks on the `UserDashboard`.
- **Reward Scaling**: Adjusted Tier thresholds (Silver: 300, Gold: 1000) for faster progression.

## 📍 System State
- **Backend**: Port 8000. Coverage >80% (Notifications added).
- **Frontend**: Port 5173. Notifications enabled. Sidebar resizable.
- **Tests**: All backend tests passed. Browser verification success.

## 🚧 Active Tasks
1. **Reward Hub UI Polish**: Finalize Reward Hub aesthetic improvements (Next).
2. **Task Import/Export UI**: Finalize modal design based on `import_wizard` logic.

## ⚠️ Known Issues / Watchlist
- **Migration Edge Cases**: `SQLAlchemy` auto-migrations are limited; use `alembic` for complex schema changes.
- **Timezone**: "Europe/Berlin" set in config but relies on system time in some Docker contexts.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — Gamification Polish is complete. Let's proceed with **Reward Hub UI Polish**."
