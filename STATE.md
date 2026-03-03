# State & Global Memory

**Librarian**: Agent-Librarian
**Last Updated**: 2026-03-03 20:51

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We have completed **System Polish & Hardening** (V1.4), **Negative Points**, **Email Notifications** (V1.6), and **Frontend Integration**. Database schema version is **1.8**.

## 🔄 Recent Changes (2026-02-27 Auth Migration & Security)
- **Secrets Auto-Generation**: JWT Secret Keys and VAPID keys are auto-generated on startup if missing, removing the need for committed secrets.
- **PIN Hashing**: Moved all user PINs to `bcrypt`. Plaintext 4-digit PINs are seamlessly intercepted and migrated to secure hashes on login.
- **VAPID Integration**: Configured `pywebpush` and `py-vapid` in the backend. Handled `VAPID_PUBLIC_KEY` loading via `python-dotenv`.
- **Database Schema**: Added `PushSubscription` model mapped to user relationships (v1.9 schema).
- **Service Worker**: Added `sw.js` for handling incoming push events and displaying browser notifications.
- **Frontend Toggle**: Added a Push Notifications toggle in the SettingsPage utilizing the `PushManager` browser API.
- **User Management Endpoints**: Completed Admin control endpoints for `Edit User` and `Delete User`, managing deep FK cleanups.
- **Background Dispatch**: Background tasks integrated to conditionally push to user endpoints on events like task completion or daily reminders.

## 🔄 Recent Changes (2026-03-03 Persistent File Storage)
- **Docker Volumes**: Added `chores_uploads` and `chores_backups` named volumes in `docker-compose.yml` so uploaded photos and database backups persist across container restarts.
- **Dockerfile**: Pre-creates `/app/uploads` and `/app/backups` directories with correct non-root ownership.
- **Production Secrets Hardening**: Upgraded auto-generated secret logs from INFO to WARNING in `security.py` and `notifications_service.py`. Documented all production env vars (`JWT_SECRET_KEY`, `VAPID_*`, `SMTP_*`, `CORS_ORIGINS`) as commented references in `docker-compose.yml`.

## 🔄 Recent Changes (2026-03-02 Deletion Modal UI Polish)
- **Modal Dark-Mode Fix**: Hardcoded dark text colors (`#1a1a2e`, `#333`, `#c53030`) inside the Delete User confirmation modal to resolve white-on-white text caused by CSS variables resolving incorrectly inside the always-white `.modal-content`.
- **Self-Deletion Prevention**: Admin's own Delete button is now `disabled` with tooltip "Cannot delete yourself".
- **Button Style Consistency**: Reverted Delete/Deduct Points buttons to match the standard `btn-secondary btn-sm` style (same as Edit).

## 📍 System State
- **Backend**: Port 8000. **135+ tests passed**. Flake8 and Mypy clean. Schema v1.9.
- **Frontend**: Port 8080 (Docker), 5173 (local). ESLint clean. Build successful.
- **Docker**: Secure configuration operational.

## 🚧 Active Tasks (Next Priority)
1. **Analytics**: Implement family progress heatmaps.
2. **Database Migration**: Fully transition from SQLite to PostgreSQL for production stability.

## ⚠️ Known Issues / Watchlist
- ~~**File Storage**: Uploads stored locally (`backend/uploads`) — must be mapped to a persistent volume in production Docker config.~~ ✅ Resolved.
- ~~**Production Secrets**: The backend `SECRET_KEY` in `backend.security` must be overwritten via environment variables before production deployment.~~ ✅ Resolved — auto-generates with WARNING logs; all env vars documented in `docker-compose.yml`.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — User Management implementation (Edit/Delete) is complete. Let's tackle the next priority task: Analytics & Heatmaps."
