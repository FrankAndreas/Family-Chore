# State & Global Memory

**Librarian**: Agent-Librarian
**Last Updated**: 2026-02-22 19:46

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We have completed **System Polish & Hardening** (V1.4), **Negative Points**, **Email Notifications** (V1.6), **Device Photo Upload**, and a full **Code & Spec Review** fixing doc drift, bugs, upload safety, and code quality issues. Schema version is now **1.7**.

## 🔄 Recent Changes (2026-02-23 Router Refactor)
- **A1: Monolithic main.py** — Split `backend/main.py` into 7 modular APIRouters (`auth`, `users`, `roles`, `tasks`, `rewards`, `transactions`, `system`).
- **A1 Extracted components** — `EventBroadcaster` moved to `backend/events.py`.
- **Testing environment** — Verified that 133 tests pass unchanged via PYTHONPATH mapping.
- **Prior Session** — B1 (Boolean Columns) and B2 (Orphaned Transactions) fixes.

## 📍 System State
- **Backend**: Port 8000. **133 tests passed**. Flake8 and Mypy clean. Schema v1.7.
- **Frontend**: Port 8080 (Docker), 5173 (local). ESLint clean.
- **Docker**: Secure configuration operational.

## 🚧 Active Tasks (Next Priority)
1. **A3**: Add return-type annotations to `crud.py`
2. **A2/M2**: DRY instance-generation logic + align dedup
3. **M4**: Typed `SplitRedemptionResponse`
4. **M3**: Reward update/delete endpoints
5. **M1**: CORS env-configurable origins

## ⚠️ Known Issues / Watchlist
- **Security (Deferred Sprint)**: PINs stored in plaintext (S1) and no auth middleware (S2). These are the highest priority but require a dedicated sprint.
- **File Storage**: Uploads stored locally — must be mapped to a persistent volume in production.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — The A1 router refactor is complete. Let's continue with A3 (return-type annotations), M1-M4 minor features, or jump to the Security Phase (S1/S2)."
