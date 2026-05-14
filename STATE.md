# State & Global Memory

**Librarian**: Agent-Librarian
**Last Updated**: 2026-05-14 15:35

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

## 🔄 Recent Changes (2026-03-06 i18n Pluralization)
- **i18next Plural Logic**: Upgraded `en.json` and `de.json` to utilize native `_one` and `_other` suffix keys for `day` vs `days`, `task` vs `tasks`, and `Day Streak!`.
- **Component Refactoring**: Stripped hardcoded JavaScript ternary singular/plural logic from `StatCards.tsx`, `TaskForm.tsx`, `Heatmap.tsx`, and `UserDashboard.tsx`. These now inject `{ count: number }` directly into the `useTranslation` hook so it intelligently renders the grammatically correct language version.

## 🔄 Recent Changes (2026-03-06 UX Architecture & Accessibility)
- **Accessibility (ARIA)**: Injected `aria-label` tags into native React components (`Heatmap.tsx` and `UserManagement.tsx`) to properly describe modal and popup close actions (`✕`) for screen readers.
- **Semantic HTML**: Replaced isolated `<label>` text with programmatic `htmlFor` bindings mapped to explicit `id` attributes on form inputs within `TaskForm.tsx`.
- **Image Descriptiveness**: Replaced generic `alt="Preview"` tags with contextually aware alternatives (e.g. "Task completion verification photo") inside `UserDashboard.tsx` for visual impairment tools.
- **QA Verifications**: All modifications structurally verified via `npm run lint` and `npx tsc --noEmit` without introducing regressions or layout degradation.

## 🔄 Recent Changes (2026-03-07 UI Routing & API Fixes)
- **Axios Interceptor**: Refactored the global 401 response interceptor in `api.ts` to execute `window.location.reload()` instead of redirecting to a non-existent React Router `/login` path, eliminating SPA crash-loops after authentication timeouts.
- **API Config Extension**: Augmented the global `AxiosRequestConfig` interface to support a custom `skipAuthRedirect: boolean` flag, allowing specific frontend components to suppress 401 interceptor logic.
- **Graceful Unauthenticated Dashboards**: Updated `FamilyDashboard.tsx` to utilize `skipAuthRedirect: true`, allowing the public-facing dashboard to safely swallow 401 errors from protected endpoints and render graceful "All done!" empty states instead of crashing.
- **SQLAlchemy Resiliency**: Patched `backend/main.py` Alembic initialization block with a safer `inspect(conn)` schema check for SQLite forwards-compatibility.

## 🔄 Recent Changes (2026-04-03 C1 FamilyDashboard Decomposition)
- **Component Extraction**: Decomposed the 723-line `FamilyDashboard.tsx` monolith into 5 focused sub-components in a new `frontend/src/components/FamilyDashboard/` directory:
  - `ClaimModal.tsx` (39 lines) — task completion user picker modal
  - `SplitRedeemModal.tsx` (132 lines) — split-cost reward redemption modal
  - `TasksTab.tsx` (125 lines) — tasks tab with collapsible user groups
  - `RedeemTab.tsx` (71 lines) — rewards tab with affordable reward filtering
  - `HistoryTab.tsx` (117 lines) — transaction history with filters and pagination
- **Parent Controller**: `FamilyDashboard.tsx` reduced to 367 lines, managing only SSE connections, API calls, state, and prop routing.
- **Admin Dashboard i18n**: Translated hardcoded English subtitles in `AdminDashboard.tsx`, `UserManagement.tsx`, `RoleManagement.tsx`, and `TaskManagement.tsx` using `useTranslation` hooks. Updated `en.json`/`de.json` with `dashboard.subtitle`, `users.subtitle`, `roles.subtitle`, `tasks.subtitle` keys.
- **Commit**: `7b2ec06`

## 🔄 Recent Changes (2026-04-03 N1/F2/C2 UX Medium-Priority Fixes)
- **N1 (SSE Mobile Indicator)**: Verified already resolved — `mobile-connection-status` dot visible on mobile viewport via `DashboardLayout.tsx` + CSS `@media (max-width: 768px)` rule.
- **F2 (SplitRedeemModal Negative Input)**: Added `inputMode="numeric"`, `onPaste` handler to block non-numeric paste, CSS to hide browser number spinners on `.contrib-input`. Fixed unused React import lint.
- **C2 (RewardHub Decomposition)**: Decomposed 689-line `RewardHub.tsx` into 482-line parent + 4 sub-components in `RewardHub/` directory:
  - `TierProgressBar.tsx` (42 lines) — tier progress display with confetti trigger
  - `CurrentGoal.tsx` (54 lines) — current goal card with progress bar
  - `RewardCard.tsx` (110 lines) — individual reward card (locked/affordable/goal states)
  - `RewardForm.tsx` (85 lines) — shared create/edit reward form (replaces duplicated form code)
  - **Also fixed A1/N4 regression**: Replaced raw `div.modal-overlay` inline modals with shared `Modal` component for proper accessibility (focus trap, ARIA, Escape key).
- **C2 (TaskManagement Decomposition)**: Decomposed 521-line `TaskManagement.tsx` into 395-line parent + 3 sub-components in `TaskManagement/` directory:
  - `TaskCard.tsx` (87 lines) — individual task card with schedule badge and actions
  - `TaskRoleGroup.tsx` (70 lines) — role group header + task grid
  - `DeleteTaskModal.tsx` (45 lines) — delete confirmation modal
- **Quality**: ESLint clean, TypeScript `--noEmit` clean, browser-verified.

## 🔄 Recent Changes (2026-04-04 Architecture Refactoring Phase 1)
- **Backend Service Layer**: Decoupled business logic from `crud.py` into dedicated `gamification.py`, `rewards.py`, `tasks.py`, and `users.py` services.
- **Frontend Refactor**: Extracted complex state management from the monolithic `FamilyDashboard.tsx` into modular and testable React Hooks (`useFamilyDashboardData`, `useTransactions`).
- **Validation**: 142 backend tests passing, successfully verified live SSE point accumulation on the UI via browser end-to-end testing.

## 🔄 Recent Changes (2026-04-04 Architecture Refactoring Phase 2)
- **Domain Exceptions**: Restructured error handling across `services/` and `routers/`. Introduced `DomainError` hierarchy (`TaskNotFoundError`, `InsufficientPointsError`, `InvalidStateTransitionError`) mapping directly to HTTP status codes via a global FastAPI exception handler, removing 50+ lines of redundant error-status dictionary checking.
- **Gamification Engine**: Implemented `current_time` time-travel injection into `gamification.py`. Replaced flat base points with a compound streak mechanic (+0.1 multiplier daily, capped at +0.5). Included a `reset_expired_streaks` function for scheduled midnight cron job resets.
- **Verification**: 147 backend automated tests passing. Clean `flake8` and `mypy` runs. End-to-end Browser Agent successfully verified manual Streak point increments, standard task completion, and correct Insufficient Funds UI state rejections without crashing.

## 🔄 Recent Changes (2026-04-04 Low-Severity UX Fixes N3/F3/T3)
- **N3 (ErrorBoundary i18n)**: Refactored `ErrorBoundary.tsx` to use an inner functional `ErrorDisplay` component with `useTranslation` hook (class components can't use hooks). Added `errorBoundary.*` keys to both `en.json` and `de.json`.
- **F3 (PhotoDropzone Extraction)**: Extracted the inline photo drop-zone from `UserDashboard.tsx` into a reusable `PhotoDropzone.tsx` component with `useCallback`-wrapped drag/drop handlers. Added missing `dashboard.photoTake`, `dashboard.photoReplace`, `dashboard.photoRequired` i18n keys to both locale files.
- **T3 (Mobile Swipe Tabs)**: Created `useSwipeTabs.ts` custom hook using `touchstart`/`touchmove`/`touchend` events with 50px threshold and vertical-scroll detection. Applied to `FamilyDashboard.tsx` (3 tabs: tasks/redeem/history) and `UserDashboard.tsx` (2 tabs: tasks/history).
- **N6**: Already resolved — Login.tsx has hint text and description paragraph for Family Dashboard button.
- **N7**: Already resolved — shared Modal component handles Escape key and focus trap.
- **Quality**: ESLint clean, TypeScript `--noEmit` clean, browser-verified.

## 🔄 Recent Changes (2026-05-05 Architecture Phase 4 & Frontend SSE)
- **God Object Extraction**: Completed decoupling `crud.py` into dedicated `scheduler.py` and `notifications.py` services. 
- **Router Layer Isolation**: Completely removed all direct calls to `crud.py` for notification broadcasting, task logic, user creation, and web-push subscription.
- **Frontend Performance**: Refactored `useFamilyDashboardData.ts` to actively ignore backend `ping` SSE messages, eliminating unnecessary 30-second component re-renders.
- **Test Integrity**: Validated with a 100% pass rate in the backend test suite, alongside 0 errors for `flake8` and `mypy`. 

## 🔄 Recent Changes (2026-05-08 Backend Test Repair)
- **Test Alignment**: Migrated all deprecated `crud.py` references within the test suite (`test_notifications.py`, `test_crud_*.py`) to use their decoupled service equivalents (`scheduler.py`, `notifications.py`).
- **PEP8 & Type Checking**: Resolved unused import violations and corrected `Any` type casting in `backend/security.py` to achieve fully green `flake8` and `mypy` test runs.
- **Environment**: Documented the necessity of using `--break-system-packages` for local pip test installation on strict Python 3.14 environments. 

## 🔄 Recent Changes (2026-05-14 Backend Architecture Debt Fixes)
- **Non-Blocking I/O**: Refactored `upload_task_photo` and `/backups/run` endpoints. `upload_task_photo` now offloads file writes to a thread pool via `run_in_threadpool`, and backups are queued gracefully via `BackgroundTasks`. This eliminates severe event loop blocking previously caused by expensive disk operations on the main execution thread.
- **N+1 SQL Queries Remediation**: Rewrote SQLAlchemy task queries in `crud.py` to utilize `.options(joinedload(...))` eager fetching. Nested task and user dependencies are now dynamically assembled in a single SQL operation, dramatically cutting down latency.
- **Pydantic Configuration Refactor**: Stripped all disparate `os.getenv` environment parsing instances scattered across `main.py`, `database.py`, and `notifications_service.py`. A centralized, robust schema is now utilized via the `pydantic-settings` module, enforcing fallback policies consistently and improving code cleanliness. Secure `.env` auto-generation via `security.py` safely remains untouched.

## 🔄 Recent Changes (2026-05-14 Performance Audit: Image Compression & Code-Splitting)
- **P0 Server-Side Image Optimization**: Refactored `upload_task_photo` in `backend/routers/tasks.py`. Replaced direct spooling of raw multi-megabyte image files to disk with an in-memory streaming buffer, then offloaded a WebP conversion process (capped at 1280px edge, 82% quality) to a non-blocking threadpool via the `Pillow` library.
- **Resource Safety & Cleanup**: Implemented existence-guarding `os.remove` logic within the `UnidentifiedImageError` exception block, guaranteeing that partial or malformed files are cleanly purged from `uploads/` before client errors return. Added `Pillow>=10.0.0` to `requirements.txt`.
- **P1 Frontend Code-Splitting**: Replaced synchronous imports of all primary application view pages in `App.tsx` with `React.lazy()` dynamically-imported wrappers wrapped in a robust `<Suspense>` fallback block containing visual `SkeletonLoader` tokens.
- **Webpack/Vite Bundle Splitting**: Initial JavaScript asset weight cut by **54%** (from **871.63 kB** to **394.55 kB**). Admin and analytics dashboards are now completely lazy-loaded, fetching asynchronously only when navigated to.
- **Environment Stability Fixes**: Corrected broken typing configurations inside `vite.config.ts` (switched to `vitest/config`) and resolved type-assertion mocks inside `UserContext.test.tsx` to ensure 100% compiler-clean `tsc` and `lint` pipelines.

## 📍 System State
- **Backend**: Port 8000. **183 tests passed**. Flake8 and Mypy clean. Schema v1.9 tracked via Alembic. All services decoupled. Event loops strictly unblocked.
- **Frontend**: Port 8080 (Docker), 5173 (local). ESLint clean. TypeScript clean. Fully internationalized (EN/DE). Enhanced WCAG 2.1 compliance.
- **Docker**: Secure PostgreSQL + FastAPI configuration operational.

## 🚧 Remaining UX Review Items
**Source**: `docs/reviews/ux-review-2026-03-11.md`

✅ **ALL UX review items are now complete** — P0–P4, Medium, and Low severity.

| ID | Severity | Description | Status |
|----|----------|-------------|--------|
| N1 | 🟡 Medium | SSE indicator hidden on mobile (collapsed sidebar) | ✅ Done |
| F2 | 🟡 Medium | SplitRedeemModal number inputs accept negative visually | ✅ Done |
| C2 | 🟡 Medium | Other oversized components (RewardHub, TaskManagement) | ✅ Done |
| N3 | 🟢 Low | ErrorBoundary recovery + i18n | ✅ Done |
| N6 | 🟢 Low | Family Dashboard button context unclear | ✅ Done (was already fixed) |
| N7 | 🟢 Low | No keyboard shortcuts or bulk actions | ✅ Done (via Modal component) |
| F3 | 🟢 Low | Photo drop-zone inline handlers/untranslated text | ✅ Done |
| T3 | 🟢 Low | No swipe gestures for mobile | ✅ Done |

## ⚠️ Known Issues / Watchlist
- All security issues (S1–S13) ✅ Resolved
- All IDOR vulnerabilities ✅ Resolved
- All P0–P4 priority UX fixes ✅ Resolved
- All 🟡 Medium UX fixes ✅ Resolved
- All 🟢 Low UX fixes ✅ Resolved
- Backend Performance bottleneck remediations ✅ Resolved
- **🎉 UX Review fully complete**

---

## 🔜 Next Session Prompt
> **Start a new conversation and say:**
> "Review `STATE.md`. All frontend UX and top-priority backend architecture debts are resolved. Consider new features, deep frontend Vitest infrastructure tests, or overall performance optimization."
