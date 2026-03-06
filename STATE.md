# State & Global Memory

**Librarian**: Agent-Librarian
**Last Updated**: 2026-03-05 07:23

## 🧠 Global Context
The project is a **Family Chore Gamification System** (Universal-GSD-Core). We have completed **System Polish & Hardening** (V1.4), **Negative Points**, **Email Notifications** (V1.6), **Frontend Integration**, **Analytics & Heatmaps**, and **Security Hardening**. Database schema version is **1.9**.

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

## 🔄 Recent Changes (2026-03-05 Security Hardening Sprint)
- **S2**: Seed data now hashes admin PIN with bcrypt via `security.get_password_hash()` before DB insert.
- **S3**: SSE `/events` endpoint requires JWT (passed via `?token=` query param due to EventSource API limitations).
- **S4**: `/backups/run` endpoint secured with `Depends(get_current_admin_user)`.
- **S7–S10**: IDOR vulnerabilities fixed — reward redemption, notification read/mark-read, goal-setting, and language update all derive `user_id` from JWT instead of accepting it as a parameter.
- **S12**: Login error messages unified to `401 "Invalid credentials"` to prevent user enumeration.
- **S13**: Push unsubscribe verifies subscription ownership via new `crud.delete_push_subscription_by_user()`.
- **E4**: All scheduler `SessionLocal()` calls wrapped in `try/finally` to prevent DB session leaks.
- **Frontend**: Updated `api.ts`, `RewardHub.tsx`, `NotificationContext.tsx`, `FamilyDashboard.tsx` to match new backend API contracts.
- **Tests**: All 142 passing. BDD feature file and unit tests updated for new error messages and removed `user_id` params.

## 🔄 Recent Changes (2026-03-06 UX Polish & i18n Completion)
- **Internationalization**: Fully extracted all remaining hardcoded English strings into `en.json` and `de.json` across all admin and user dashboards, modals, settings, and forms.
- **UX performance**: Implemented bounded pagination (Load More) for history tabs to prevent excessive DOM rendering on accounts with long transaction histories.
- **Debounced Search**: Integrated a custom `useDebounce` hook (300ms delay) for the transaction filtering inputs, vastly reducing rapid React re-renders and potential API spam.
- **Memory Management**: Fixed an `ObjectURL` memory leak in `UserDashboard` where photo thumbnails weren't properly revoked if unmounted quickly. Delegated lifecycle solely to `PhotoPreview` components.

## 🔄 Recent Changes (2026-03-06 Security S5: Auth Uploads)
- **Backend Route**: Removed the public `StaticFiles` mount for `/uploads/` and replaced it with a custom FastAPI endpoint secured by `Depends(get_current_user)`.
- **HttpOnly Cookies**: Upgraded `auth.py` to issue an `HttpOnly` cookie containing the `access_token` upon login. Upgraded `dependencies.py` to extract this cookie as a fallback if the `Authorization` header is missing.
- **Frontend Axios**: Enabled `withCredentials: true` globally so cross-origin requests attach the secure cookie, allowing standard `<img src="/uploads/XYZ">` tags to seamlessly bypass 401s in authenticated sessions.

## 🔄 Recent Changes (2026-03-06 Database Migration)
- **Alembic Integration**: Replaced custom Python migration scripts with `alembic` for standardized schema management. Generated baseline migration `v1.9`.
- **Dual-Dialect Support**: Updated `backend/database.py` and `backend/main.py` to seamlessly execute schema migrations natively on PostgreSQL while seamlessly falling back to local SQLite execution (and backwards compatible dynamic stamping) based on the `DATABASE_URL` environment variable.
- **Docker Infrastructure**: Modified `docker-compose.yml` to provision a persistent `postgres:15-alpine` container and wired the backend to connect natively.
- **Testing**: `run_tests.sh` isolates the test suite from Alembic locking via `TESTING=True` env variable, relying on in-memory SQLite schema creation. Migration scripts excluded from `flake8` to prevent PEP8 noise.

## 📍 System State
- **Backend**: Port 8000. **142 tests passed**. Flake8 and Mypy clean. Schema v1.9 tracked via Alembic.
- **Frontend**: Port 8080 (Docker), 5173 (local). ESLint clean. Build successful. Fully internationalized (EN/DE).
- **Docker**: Secure PostgreSQL + FastAPI configuration operational.

## 🚧 Active Tasks (Next Priority)
1. **Pluralization**: Handle singular/plural forms (e.g., "1 Tag" vs "2 Tage") via i18next `count` interpolation.

## ⚠️ Known Issues / Watchlist
- ~~**S5**: `/uploads/` directory is publicly accessible without authentication.~~ ✅ Resolved.
- ~~**IDOR vulnerabilities**: S7–S10, S13 — user_id params allowed cross-user access.~~ ✅ Resolved.
- ~~**Login enumeration**: S12 — distinct error messages leaked user existence.~~ ✅ Resolved.
- ~~**SSE/Backup endpoints unauthenticated**: S3, S4.~~ ✅ Resolved.

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review STATE.md — Security hardening is complete. Let's tackle the next priority."
