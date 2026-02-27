# State & Global Memory

**Librarian**: Agent-Librarian
**Last Updated**: 2026-02-27 13:28

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We have completed **System Polish & Hardening** (V1.4), **Negative Points**, **Email Notifications** (V1.6), and **Frontend Integration**. Schema version is now **1.8**.

## 🔄 Recent Changes (2026-02-27 Authentication Security)
- **S1 Authentication & PINs**: Integrated `passlib[bcrypt]` to securely hash all user PINs. Migrated 56 existing plaintext PINs to hashed via `v1_8_hash_pins.py` custom migration script.
- **Login Verification**: Updated `/login/` endpoint to verify bcrypt hashes instead of direct string comparison. Fixes a critical security vulnerability. 
- **Mypy Type Casting**: Resolved SQLAlchemy `Column[str]` to `str` checking issues by using strict `typing.cast` and string coercions in auth models.
- **Test Integrity**: Validated full 136-test suite passed under strict PEP8 and automated assertions without mocking the core hashing algorithm.

## 📍 System State
- **Backend**: Port 8000. **136 tests passed**. Flake8 and Mypy clean. Schema v1.8.
- **Frontend**: Port 8080 (Docker), 5173 (local). ESLint clean.
- **Docker**: Secure configuration operational.

## 🚧 Active Tasks (Next Priority)
1. **S2**: Auth Middleware (secure API endpoints matching frontend auth state)
2. **Frontend Integration**: Hook up Web Push Notifications (Deferred V1.5 task).
3. **Analytics**: Implement family progress heatmaps.

## ⚠️ Known Issues / Watchlist
- **Security (Deferred Sprint)**: No auth middleware implemented yet (S2). Endpoints still rely on client-side role enforcement which is easily bypassed via direct API calls.
- **File Storage**: Uploads stored locally — must be mapped to a persistent volume in production.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — S1 PIN Hashing is complete. The next highest priority item is S2 (Auth Middleware). Let's implement JWTs and secure the API endpoints based on roles."
