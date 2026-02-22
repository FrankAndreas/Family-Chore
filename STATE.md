# State & Global Memory

**Librarian**: Agent-Librarian
**Last Updated**: 2026-02-21 22:20

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We have completed **System Polish & Hardening** (V1.4), implemented **Negative Points**, and just deployed **Email Notifications** (V1.6) for pending tasks and admin approvals.

## 🔄 Recent Changes (2026-02-22 Device Photo Upload)
- **Photo Upload**: Migrated task photo verification from URL-pasting to true multipart/form-data device photo capture.
- **Backend Storage**: Added a local `backend/uploads/` directory mapped via FastAPI's `StaticFiles` for serving uploaded images.
- **Frontend Capture**: Replaced text input with `<input type="file" accept="image/*" capture="environment">` to natively open mobile cameras and support file selection.

## 📍 System State
- **Backend**: Port 8000. 132 tests passed (including new notification background and API tests). Flake8 and Mypy clean.
- **Frontend**: Port 8080 (Docker), 5173 (local). Settings tab implemented. ESLint clean.
- **Docker**: Secure configuration operational.
- **Tests**: QA verification complete for Docker containers and UI updates.

## 🚧 Active Tasks
1. **Security Hardening**: Address deferred security tasks (C1, C2, C4, L4). Top priority is Auth/PIN management.

## ⚠️ Known Issues / Watchlist
- **Security Check**: The app currently stores PINs in plaintext and lacks authentication middleware. This is the top priority for the next session.
- **File Storage**: Uploads are stored locally. In a stateless containerized runtime, `backend/uploads/` must be mapped to a persistent volume bind to avoid breaking images on container restart.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — Device Photo Upload is complete. Let's proceed with the Security Phase to address plaintext PINs and authentication."
