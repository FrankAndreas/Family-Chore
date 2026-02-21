# State & Global Memory

**Librarian**: Agent-Librarian
**Last Updated**: 2026-02-21 22:20

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We have completed **System Polish & Hardening** (V1.4), implemented **Negative Points**, and just deployed **Email Notifications** (V1.6) for pending tasks and admin approvals.

## 🔄 Recent Changes (2026-02-21 Email Notifications)
- **Email Notifications**: Added `email` and `notifications_enabled` to `User` model with DB migrations.
- **Background Mailer**: Implemented `send_email_background` using FastAPI `BackgroundTasks` with SMTP fallback to local terminal logging.
- **Triggers**: Nightly cron job emails users with pending daily tasks. Admin gets email when a task is completed "IN_REVIEW" (e.g., photo upload).
- **Settings UI**: Added Settings tab in `UserDashboard` for users to manage their email and notification toggle.

## 📍 System State
- **Backend**: Port 8000. 132 tests passed (including new notification background and API tests). Flake8 and Mypy clean.
- **Frontend**: Port 8080 (Docker), 5173 (local). Settings tab implemented. ESLint clean.
- **Docker**: Secure configuration operational.
- **Tests**: QA verification complete for Docker containers and UI updates.

## 🚧 Active Tasks
1. **Security Hardening**: Address deferred security tasks (C1, C2, C4, L4). Top priority is Auth/PIN management.

## ⚠️ Known Issues / Watchlist
- **Security Check**: The app currently stores PINs in plaintext and lacks authentication middleware. This is the top priority for the next session.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — Email Notifications are complete. Let's proceed with the Security Phase to address plaintext PINs and authentication."
