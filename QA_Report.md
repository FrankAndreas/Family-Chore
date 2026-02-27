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
