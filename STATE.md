# State & Global Memory

**Librarian**: Agent-Librarian (Model: gemini-3-flash)
**Last Updated**: 2026-02-06 21:45

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We are currently in the **Frontend Completion** phase.

## 🔄 Recent Changes (This Session)

### Family Dashboard Feature
- **Backend**: Implemented `GET /tasks/pending` and `complete_task` with `actual_user_id` for task claiming.
- **Frontend**: New "Family Dashboard" view with "Who did it?" modal.
- **Test**: `tests/test_family_claim.py` passing.

### Documentation (REORGANIZED)
- **Master Spec**: Consolidated technical truth into `docs/master-spec.md`.
- **Structure**: Implemented "Master + Guides" architecture:
  - `docs/master-spec.md`: Core truth.
  - `docs/guides/`: User-facing walkthroughs.
  - `docs/reports/`: QA/Testing results.
  - `docs/archive/`: Legacy planning/meta.

### Automatic Daily Reset (NEW)
- **Problem**: Tasks weren't appearing because the Daily Reset was manual-only.
- **Solution**: 
  1. Added `last_daily_reset` tracking in SystemSettings.
  2. Smart startup check: Only generates instances if not done today.
  3. **Midnight Scheduler**: APScheduler runs `perform_daily_reset_if_needed()` at 00:00 every day.
- **Files Changed**: `backend/main.py`, `backend/crud.py`

### Schema Enhancement
- `TaskInstance` now includes `task` and `user` relationships for richer API responses.

## 📍 System State
- **Backend**: Running on Port 8001. Scheduler active.
- **Frontend**: Running on Port 5173.
- **Database**: Functional with `last_daily_reset` tracking.

## 🚧 Active Tasks
1. **Reward Hub UI**: Needs visual implementation.
2. **Compliance Reports**: Needs UI graphs.

## ⚠️ Known Issues / Watchlist
- None currently. Daily reset is now automatic.

## 📝 New Dependencies
- `apscheduler` added to `backend/requirements.txt`

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**  
> "As Librarian, update STATE.md and LEARNINGS.md with the workflow improvements we made."

*This field is updated by the Librarian at the end of each session to guide the next agent.*
