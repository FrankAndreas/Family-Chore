# State & Global Memory

**Librarian**: Agent-Librarian
**Last Updated**: 2026-03-04 21:18

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

## 🔄 Recent Changes (2026-03-04 Analytics & Heatmaps)
- **Backend Endpoints**: Added `GET /analytics/heatmap` (per-user daily task counts), `GET /analytics/summary` (weekly totals, top performer, streak leaderboard), and `GET /analytics/heatmap/details` (task drill-down for a specific user+date).
- **Pydantic Schemas**: 8 new schemas (`HeatmapDay`, `UserHeatmap`, `HeatmapResponse`, `HeatmapTaskDetail`, `HeatmapDayDetails`, `StreakInfo`, `TopPerformer`, `AnalyticsSummary`).
- **Frontend Components**: `StatCards` (animated count-up stat cards), `Heatmap` (custom CSS Grid with clickable cells and task detail popup), `TimeRangeSelector` (Grafana-style 7d/14d/30d/60d/90d presets).
- **Dashboard Integration**: `AnalyticsDashboard.tsx` now fetches all 4 data sources in parallel and renders stat cards → charts → heatmaps.
- **Tests**: 5 analytics-specific tests (weekly, distribution, heatmap, summary, details). Full suite: **142 tests passing**.
- **Docs**: Updated `user-guide.md` with new analytics features.

## 🔄 Recent Changes (2026-03-04 i18n Expansion — Analytics German)
- **German Translations**: Added 19 analytics keys to `de.json` covering StatCards, TimeRangeSelector, and Heatmap.
- **English Translations**: Added 13 missing analytics keys to `en.json` for completeness.
- **Interpolation Fix**: Refactored `AnalyticsDashboard.tsx` `family_heatmap` to use i18next `{{ }}` interpolation instead of JS template literal.
- **BDD Spec**: Added §4.7 Analytics Localization scenario to `master-spec.md`.
- **Docs**: Updated `user-guide.md` with Time Range Selector and Language Support notes.
- **QA**: Browser-verified all 10 German labels render correctly on the Analytics Dashboard.

## 📍 System State
- **Backend**: Port 8000. **142 tests passed**. Flake8 and Mypy clean. Schema v1.9.
- **Frontend**: Port 8080 (Docker), 5173 (local). ESLint clean. Build successful.
- **Docker**: Secure configuration operational.

## 🚧 Active Tasks (Next Priority)
1. **Database Migration**: Transition from SQLite to PostgreSQL for production stability.
2. ~~**i18n expansion**: Add German translations for new analytics labels.~~ ✅ Completed.
3. **Pluralization**: Handle singular/plural forms (e.g., "1 Tag" vs "2 Tage") via i18next `count` interpolation.

## ⚠️ Known Issues / Watchlist
- ~~**File Storage**: Uploads stored locally (`backend/uploads`) — must be mapped to a persistent volume in production Docker config.~~ ✅ Resolved.
- ~~**Production Secrets**: The backend `SECRET_KEY` in `backend.security` must be overwritten via environment variables before production deployment.~~ ✅ Resolved — auto-generates with WARNING logs; all env vars documented in `docker-compose.yml`.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — Analytics i18n is complete. Let's tackle the next priority."
