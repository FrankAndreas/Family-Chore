# State & Global Memory

**Librarian**: Agent-Librarian
**Last Updated**: 2026-02-23 10:24

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We have completed **System Polish & Hardening** (V1.4), **Negative Points**, **Email Notifications** (V1.6), **Device Photo Upload**, and a full **Code & Spec Review** fixing doc drift, bugs, upload safety, and code quality issues. Schema version is now **1.7**.

## 🔄 Recent Changes (2026-02-23 Backend Polish)
- **M1/M3/M4**: Added CORS environment configuration (`CORS_ORIGINS`), built full CRUD endpoints for Rewards (`PUT` and `DELETE`), and provided strict Pydantic typing for `SplitRedemptionResponse` (`SplitTransactionDetail`).
- **A2/M2: DRY Task Generation** — Extracted shared `_generate_instances_for_task` helper, fixing same-day deduplication bugs.
- **A1: Monolithic main.py** — Split `backend/main.py` into 7 modular APIRouters (`auth`, `users`, `roles`, `tasks`, `rewards`, `transactions`, `system`), extracting `EventBroadcaster`.
- **A3: Return-Type Annotations** — Added return types to `backend/crud.py` functions, fixing downstream typing errors.
- **Prior Session** — B1 (Boolean Columns) and B2 (Orphaned Transactions) fixes.

## 📍 System State
- **Backend**: Port 8000. **133 tests passed**. Flake8 and Mypy clean. Schema v1.7.
- **Frontend**: Port 8080 (Docker), 5173 (local). ESLint clean.
- **Docker**: Secure configuration operational.

## 🚧 Active Tasks (Next Priority)
1. **S1**: Authentication & PINs (hash plaintext PINs)
2. **S2**: Auth Middleware (secure API endpoints matching frontend auth state)
3. **Frontend Integration**: Hook up the new Reward edit/delete UI to the new M3 endpoints.

## ⚠️ Known Issues / Watchlist
- **Security (Deferred Sprint)**: PINs stored in plaintext (S1) and no auth middleware (S2). These are the highest priority but require a dedicated sprint.
- **File Storage**: Uploads stored locally — must be mapped to a persistent volume in production.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — The M1, M3, and M4 backend tasks are complete. Let's either hook up the frontend Reward UI to use the new M3 endpoints, or jump into the Security Phase (S1/S2)."
