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
