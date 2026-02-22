# State & Global Memory

**Librarian**: Agent-Librarian
**Last Updated**: 2026-02-22 19:46

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We have completed **System Polish & Hardening** (V1.4), **Negative Points**, **Email Notifications** (V1.6), **Device Photo Upload**, and a full **Code & Spec Review** fixing doc drift, bugs, upload safety, and code quality issues. Schema version is now **1.7**.

## 🔄 Recent Changes (2026-02-22 Code Review Fixes)
- **B1: Boolean Columns** — Converted `requires_photo_verification`, `notifications_enabled`, and `Notification.read` from `Column(Integer)` to `Column(Boolean)` in models, updated schemas to use `bool`, and updated all comparisons to `.is_(True)`/`.is_(False)`.
- **B2: Orphaned Transactions** — `delete_task()` now nulls `Transaction.reference_instance_id` before deleting instances, preventing dangling foreign keys.
- **Review Fixes** — Added per-user try/except in scheduler email loop; added dedicated test for B2 orphan cleanup.
- **Prior Session** — D1-D4 (doc sync), B3 (datetime standardization), B4 (scheduler fix), S3 (upload size limit), S4 (extension trust), A4 (type rename).

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
6. **A1**: Split monolithic `main.py` into routers (largest refactor)

## ⚠️ Known Issues / Watchlist
- **Security (Deferred Sprint)**: PINs stored in plaintext (S1) and no auth middleware (S2). These are the highest priority but require a dedicated sprint.
- **File Storage**: Uploads stored locally — must be mapped to a persistent volume in production.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — Code review fixes are complete at v1.7. Let's continue with A3 (return-type annotations) or jump to the Security Phase (S1/S2)."
