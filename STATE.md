# State & Global Memory

**Librarian**: Agent-Librarian (Model: gemini-3-flash)
**Last Updated**: 2026-02-08 15:05

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We are in the **Polishing & Verification** phase — refining UI/UX and ensuring system stability.

## 🔄 Recent Changes (2026-02-10 Analytics Session)

## 🔄 Recent Changes (2026-02-11 Import Fix & Polish)

### Task Import Wizard (v1.7)
- **Localization**: Added backend support for importing tasks with German role names ("Kind", "Mitwirkender") by mapping them to system roles.
- **UI Fixes**: Fixed `ImportTasksModal` readability in Dark Mode by using semi-transparent backgrounds and proper text contrast.

### Quality Assurance
- **Unit Tests**: Added `tests/unit/test_import_tasks.py` covering 100% of the Import Wizard logic.
- **Mobile Polish**: Implemented responsive tables for mobile users.

## 📍 System State
- **Backend**: Port 8000. Verified import logic + Timezone support.
- **Frontend**: Port 5173. Mobile-ready.
- **Database**: v1.3.

## 🚧 Active Tasks
1. **Testing**: Expand unit test coverage for other modules.
2. **Backups**: Verified local backup creation.

## ⚠️ Known Issues / Watchlist
- **Zombie Processes**: Hardened shutdown logic, but keep an eye on `uvicorn` processes.
- **Timezone**: Configured to "Europe/Berlin" by default. Check logs if verified otherwise.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — Import Wizard is fully fixed (Roles + UI). Let's tackle the 'Zombie Processes' issue or Timezone support."

*This field is updated by the Librarian at the end of each session to guide the next agent.*
