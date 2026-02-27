# State & Global Memory

**Librarian**: Agent-Librarian
**Last Updated**: 2026-02-27 14:52

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We have completed **System Polish & Hardening** (V1.4), **Negative Points**, **Email Notifications** (V1.6), and **Frontend Integration**. Database schema version is **1.8**.

## 🔄 Recent Changes (2026-02-27 Auth Migration & Security)
- **Secrets Auto-Generation**: JWT Secret Keys and VAPID keys are auto-generated on startup if missing, removing the need for committed secrets.
- **PIN Hashing**: Moved all user PINs to `bcrypt`. Plaintext 4-digit PINs are seamlessly intercepted and migrated to secure hashes on login.
- **VAPID Integration**: Configured `pywebpush` and `py-vapid` in the backend. Handled `VAPID_PUBLIC_KEY` loading via `python-dotenv`.
- **Database Schema**: Added `PushSubscription` model mapped to user relationships (v1.9 schema).
- **Service Worker**: Added `sw.js` for handling incoming push events and displaying browser notifications.
- **Frontend Toggle**: Added a Push Notifications toggle in the SettingsPage utilizing the `PushManager` browser API.
- **Background Dispatch**: Background tasks integrated to conditionally push to user endpoints on events like task completion or daily reminders.

## 📍 System State
- **Backend**: Port 8000. **135+ tests passed**. Flake8 and Mypy clean. Schema v1.9.
- **Frontend**: Port 8080 (Docker), 5173 (local). ESLint clean. Build successful.
- **Docker**: Secure configuration operational.

## 🚧 Active Tasks (Next Priority)
1. **Analytics**: Implement family progress heatmaps.
2. **Database Migration**: Fully transition from SQLite to PostgreSQL for production stability.

## ⚠️ Known Issues / Watchlist
- **File Storage**: Uploads stored locally (`backend/uploads`) — must be mapped to a persistent volume in production Docker config.
- **Production Secrets**: The backend `SECRET_KEY` in `backend.security` must be overwritten via environment variables before production deployment.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — S2 Auth Middleware is complete. Let's tackle the next priority task: Web Push Notifications."
