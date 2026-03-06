# QA Report: S1 Authentication & PIN Hashing

## ✅ Tests Passed: 136
- Automated Regression Suite: 133 tests passed
- Manual API Test 1: User creation with `login_pin: "5555"` responds with HTTP 200 and stores hashed PIN.
- Manual API Test 2: User login with correct PIN (`5555`) responds with HTTP 200 and returns user object.
- Manual API Test 3: User login with incorrect PIN (`9999`) responds with HTTP 401 and "Incorrect PIN" message.

## ❌ Tests Failed: 0
- No failures observed.

## ⚠️ Edge Cases & Notes:
- Database migration script tested and functioning. Plain-text PINs correctly upgraded in `chorespec_mvp.db`.
- Using `bcrypt` via `passlib` requires type-casting the sqlalchemy string columns during model query, handled properly in the auth router.
- `Requires photo verification` column and other prior schema types unaffected.

---

# QA Report: S5 Secure File Uploads (/uploads/)

## ✅ Tests Passed: 142
- **Automated Regression Suite**: 142 tests passed perfectly across all modules.
- **Manual API Test 1 (Unauthenticated)**: GET `/uploads/test_photo.jpg` accurately rejected with HTTP 401 Unauthorized `{"detail": "Not authenticated"}`.
- **Manual API Test 2 (Authenticated Header)**: GET `/uploads/test_photo.jpg` passed with `Authorization: Bearer <token>` returning HTTP 200 OK.
- **Manual API Test 3 (Authenticated Cookie)**: GET `/uploads/test_photo.jpg` passed with `Cookie: access_token=Bearer <token>` returning HTTP 200 OK.

## ❌ Tests Failed: 0
- No failures observed.

## ⚠️ Edge Cases & Notes:
- The `FastAPI` file serving route now directly invokes `os.path.exists()` ensuring non-existent files smoothly return 404 instead of throwing internal server errors.
- Cross-origin credentials correctly enabled (`withCredentials=true`) in the frontend Axios client. 

---

# QA Report: Database Migration (PostgreSQL / SQLite Dual-Dialect)

## ✅ Tests Passed: 142 (SQLite) + Manual Verification (PostgreSQL)
- **Automated Regression Suite (SQLite)**: 142 tests passed perfectly. `TESTING=True` environment variable effectively isolates test runs from `alembic` locking mechanisms.
- **Manual Verification (PostgreSQL)**:
  - Docker Compose `db` container booted successfully (`postgres:15-alpine`).
  - `alembic upgrade head` executed perfectly against the live PostgreSQL database via `DATABASE_URL`, generating the full schema.
  - SQLAlchemy ORM connection test confirmed successful insertion and retrieval of `Role` data natively in PostgreSQL.

## ❌ Tests Failed: 0
- No failures observed. Local SQLite operations preserve backward compatibility via dynamic `alembic` stamping.

## ⚠️ Edge Cases & Notes:
- SQLite enforces `check_same_thread: False`, handled conditionally via `DATABASE_URL.startswith("sqlite")`.
- Old Python migration scripts successfully deprecated in favor of `alembic` tracking.

---

# QA Report: i18n Pluralization (EN and DE)

## ✅ Tests Passed: 142
- **Automated Regression Suite (Backend)**: 142 tests passed, confirming no backend regressions caused by frontend string changes.
- **Frontend Linting/Typing**: `npm run lint` and `npx tsc --noEmit` passed cleanly.
- **Manual Verification (English)**: Verified component rendering handles "1 day" and "3 days" singular/plural grammar correctly using i18n count interpolation.
- **Manual Verification (German)**: Verified component rendering handles "1 Tag" and "3 Tage" appropriately for stat cards, forms, and heatmaps.

## ❌ Tests Failed: 0
- No failures observed.

## ⚠️ Edge Cases & Notes:
- Removed hardcoded JavaScript ternary logic (e.g. `value === 1 ? 'day' : 'days'`) in favor of native `useTranslation` capabilities.
- Added `_one` and `_other` keys for strict plural support across `days`, `tasks`, and `dayStreak`.

# QA Report: UX & Accessibility Fixes (Phase 1)

## ✅ Tests Passed: Frontend Lint & DOM Semantics
- **Automated Verification**: `npm run lint` and `npx tsc --noEmit` executed against `frontend/src` successfully.
- **Manual Verification 1 (ARIA Close Buttons)**: `aria-label="Close modal"` and `aria-label="Close details"` successfully injected into the native React synthetic DOM representation across `<Heatmap>` and `<UserManagement>` modals.
- **Manual Verification 2 (Input-Label Binding)**: `htmlFor` attributes securely mapped to their respective `id` properties (`taskName`, `taskDescription`, `taskBasePoints`) within `<TaskForm>`.
- **Manual Verification 3 (Image Alt-Text Descriptiveness)**: Default "Preview" alt-text securely replaced with explicit, content-aware "Task completion verification photo" within `<UserDashboard>`.

## ❌ Tests Failed: 0
- No failures observed. The DOM structurally supports the enhanced WCAG 2.1 traits without degrading layout properties. 

## ⚠️ Edge Cases & Notes:
- Cross-checking `index.css` revealed existing generic `:focus` definitions are handling the outline rendering for inputs successfully.

---
