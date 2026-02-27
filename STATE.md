# State & Global Memory

**Librarian**: Agent-Librarian
**Last Updated**: 2026-02-27 14:52

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We have completed **System Polish & Hardening** (V1.4), **Negative Points**, **Email Notifications** (V1.6), and **Frontend Integration**. Database schema version is **1.8**.

## 🔄 Recent Changes (2026-02-27 Auth Middleware & JWTs)
- **S2 Auth Layer**: Implemented `PyJWT` for stateless token-based authentication, replacing insecure client-side role checks.
- **Role-Based Access Control (RBAC)**: Created `get_current_user` and `get_current_admin_user` FastAPI dependencies to lock down admin routes (Create/Edit task, Penalize user, etc.).
- **Client Integration**: Updated Axios interceptors to inject `Authorization: Bearer <token>` globally on the frontend, and handle automatic logouts on `401 Unauthorized`.
- **Test Integrity**: Patched Pytest test client with `dependency_overrides` to mock the active user during legacy tests, preserving 130+ passing tests. Verified End-to-End via standalone python script.

## 📍 System State
- **Backend**: Port 8000. **133 tests passed**. Flake8 and Mypy clean. Schema v1.8.
- **Frontend**: Port 8080 (Docker), 5173 (local). ESLint clean. Build successful.
- **Docker**: Secure configuration operational.

## 🚧 Active Tasks (Next Priority)
1. **Frontend Integration**: Hook up Web Push Notifications (Deferred V1.5 task).
2. **Analytics**: Implement family progress heatmaps.
3. **Database Migration**: Fully transition from SQLite to PostgreSQL for production stability.

## ⚠️ Known Issues / Watchlist
- **File Storage**: Uploads stored locally (`backend/uploads`) — must be mapped to a persistent volume in production Docker config.
- **Production Secrets**: The backend `SECRET_KEY` in `backend.security` must be overwritten via environment variables before production deployment.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — S2 Auth Middleware is complete. Let's tackle the next priority task: Web Push Notifications."
