# State & Global Memory

**Librarian**: Agent-Librarian
**Last Updated**: 2026-02-23 10:24

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We have completed **System Polish & Hardening** (V1.4), **Negative Points**, **Email Notifications** (V1.6), **Device Photo Upload**, and a full **Code & Spec Review** fixing doc drift, bugs, upload safety, and code quality issues. Schema version is now **1.7**.

## 🔄 Recent Changes (2026-02-23 Router Refactor)
- **A1: Monolithic main.py** — Split `backend/main.py` into 7 modular APIRouters (`auth`, `users`, `roles`, `tasks`, `rewards`, `transactions`, `system`).
- **A1 Extracted components** — `EventBroadcaster` moved to `backend/events.py`.
- **A3: Return-Type Annotations** — Added return types to `backend/crud.py` functions, fixing downstream typing errors in system routers via explicit casts.
- **Testing environment** — Verified that 133 tests pass unchanged via PYTHONPATH mapping.
- **Prior Session** — B1 (Boolean Columns) and B2 (Orphaned Transactions) fixes.

## 📍 System State
- **Backend**: Port 8000. **133 tests passed**. Flake8 and Mypy clean. Schema v1.7.
- **Frontend**: Port 8080 (Docker), 5173 (local). ESLint clean.
- **Docker**: Secure configuration operational.

## 🚧 Active Tasks (Next Priority)
1. **A2/M2**: DRY instance-generation logic + align dedup
2. **M4**: Typed `SplitRedemptionResponse`
3. **M3**: Reward update/delete endpoints
4. **M1**: CORS env-configurable origins

## ⚠️ Known Issues / Watchlist
- **Security (Deferred Sprint)**: PINs stored in plaintext (S1) and no auth middleware (S2). These are the highest priority but require a dedicated sprint.
- **File Storage**: Uploads stored locally — must be mapped to a persistent volume in production.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — A3 is complete. Let's continue with A2/M2 (DRY instance-generation), the remaining M1-M4 minor features, or jump to the Security Phase (S1/S2)."
