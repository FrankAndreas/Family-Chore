# State & Global Memory

**Librarian**: Agent-Librarian
**Last Updated**: 2026-02-21 21:55

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We have completed **System Polish & Hardening** (V1.4) and implemented the **Negative Points / Penalties** feature to allow admins to deduct points without affecting lifetime tier progress.

## 🔄 Recent Changes (2026-02-21 Negative Points & Polish)
- **Negative Points**: Implemented `POST /users/{id}/penalize` endpoint. Penalties deduct from `current_points` only and create a `PENALTY` transaction.
- **Admin UI**: Added a "Deduct Points" modal to the User Management dashboard.
- **Docker Hardening**: Both backend and frontend containers run as non-root users with optimized `.dockerignore` files.
- **UI/UX Consistency**: Global CSS `.empty-state` components.

## 📍 System State
- **Backend**: Port 8000. 130 tests passed. Flake8 and Mypy clean.
- **Frontend**: Port 8080 (via Docker), 5173 (local dev). Deduct Points and empty states implemented. ESLint clean.
- **Docker**: Secure configuration operational.
- **Tests**: QA verification complete for Docker containers and UI updates.

## 🚧 Active Tasks
1. **Security Hardening**: Address deferred security tasks (C1, C2, C4, L4). Top priority is Auth/PIN management.

## ⚠️ Known Issues / Watchlist
- **Security Check**: The app currently stores PINs in plaintext and lacks authentication middleware. This is the top priority for the next session.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — System Polish and Hardening is complete. Let's proceed with the Security Phase to address plaintext PINs and authentication."
