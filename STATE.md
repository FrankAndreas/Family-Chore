# State & Global Memory

**Librarian**: Agent-Librarian
**Last Updated**: 2026-02-21 13:48

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We have just completed a major **Code Quality & UX Refactoring** (Phases 1-4), ensuring robust type validation, bug-free components, and a clean test suite.

## 🔄 Recent Changes (2026-02-21 Photo Verification & Code Quality)
- **Photo Verification Flow**: `requires_photo_verification` triggers `IN_REVIEW` status, relying on an Admin Review Queue for approval. Fixed query-param data leak by moving photo uploads to JSON body requests.
- **Frontend Refactoring**: Addressed React anti-patterns (mutating state, shared inputs) to prevent race conditions and improve UX (Toast over blocking `alert`).
- **Data Integrity**: Enforced SQLite text-to-integer boolean conversions safely via migration.
- **Validation**: Strict typings added (mypy), deprecated Pydantic v1 methods removed.

## 📍 System State
- **Backend**: Port 8000. Coverage >78%. All 128 tests passed. Flake8 and Mypy clean.
- **Frontend**: Port 5173. Admin Review Queue and robust modals verified. ESLint and TypeScript clean.
- **Tests**: QA verification complete with real-world API assertions.

## 🚧 Active Tasks
1. **Security Hardening**: Address deferred security tasks (C1, C2, C4, L4).

## ⚠️ Known Issues / Watchlist
- **Security Check**: The app currently stores PINs in plaintext and lacks authentication middleware. This is the top priority for the next session.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — Code Quality and UI refactoring is complete. Let's proceed with the Security Phase to address plaintext PINs and authentication."
