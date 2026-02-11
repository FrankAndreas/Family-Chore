# State & Global Memory

**Librarian**: Agent-Librarian (Model: gemini-3-flash)
**Last Updated**: 2026-02-08 15:05

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We are in the **Polishing & Verification** phase — refining UI/UX and ensuring system stability.

## 🔄 Recent Changes (2026-02-10 Analytics Session)

## 🔄 Recent Changes (2026-02-11 Import Wizard Fix)

### Task Import Wizard (v1.6)
- **Backend**:
  - Enhanced `TaskImportItem` to support localized schedule types ("täglich", "wöchentlich").
  - Implemented smart conversion: Weekly tasks with specific times (HH:MM) auto-convert to recurring tasks.
- **Frontend**:
  - Improved `ImportTasksModal` error handling to show detailed validation messages.
  - Fixed Dark Mode readability for error messages.

## 📍 System State
- **Backend**: Port 8000. Import Wizard enhanced.
- **Frontend**: Port 5173. Dark Mode fixes applied.
- **Database**: v1.3.

## 🚧 Active Tasks
1. **Unit Tests**: Add tests for new import logic (currently verified via script).
2. **Mobile Polish**: Continue refining UI for mobile users.

## ⚠️ Known Issues / Watchlist
- **Zombie Processes**: `uvicorn` sometimes hangs on port 8000.
- **Timezone**: Scheduler runs on server time.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — Import Wizard is fixed. Let's move to the 'Active Task' of adding Unit Tests or polishing Mobile UI."

*This field is updated by the Librarian at the end of each session to guide the next agent.*
