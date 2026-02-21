# State & Global Memory

**Librarian**: Agent-Librarian (Model: gemini-3-flash)
**Last Updated**: 2026-02-08 15:05

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We are in the **Polishing & Verification** phase — refining UI/UX and ensuring system stability.

## 🔄 Recent Changes (2026-02-21 Task Import/Export & Photo Verification)
- **Photo Verification**: Added `requires_photo_verification` to `Task` model. Implemented an `IN_REVIEW` status for tasks requiring photos, with an Admin Review Queue for approvals/rejections before points are awarded.
- **Import/Export Reliability**: Fixed boolean coercion issues where SQLite `Text` fields representing booleans ('true', '1') were causing Pydantic validation errors during import/export.

## 📍 System State
- **Backend**: Port 8000. Coverage >77%. All 128 tests passed.
- **Frontend**: Port 5173. Photo upload UI and Admin Review Queue verified. All linting/typechecks passing.
- **Tests**: Full backend regression suite passed successfully. Frontend static analysis clean.

## 🚧 Active Tasks
1. **System Refinement**: Await next feature assignment from Product Owner.

## ⚠️ Known Issues / Watchlist
- **Migration Edge Cases**: `SQLAlchemy` auto-migrations are limited; use `alembic` for complex schema changes.
- **Timezone**: "Europe/Berlin" set in config but relies on system time in some Docker contexts.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — Photo Verification and Import/Export fixes are complete. Let's proceed with the next feature."
