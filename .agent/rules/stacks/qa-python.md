---
trigger: glob
globs: **/*.py
---

# Python Testing Standards (Pytest)

- **Library:** Use `pytest` for all backend tests.
- **Fixtures:** Define shared fixtures in `conftest.py`. Do not duplicate setup code.
- **Mocking:** Prefer `unittest.mock.patch` as a decorator.
- **Async:** Use `pytest-asyncio` for async route testing.
- **Command:** Run tests using `PYTHONPATH=. pytest -v` from the project root.
- **Test Databases:** Always use `sqlite:///:memory:` with `Base.metadata.create_all()` for clean test DBs. Never depend on persistent test database files — stale schemas cause phantom failures.
- **Narrow Try Blocks:** Keep `try/except` scopes as small as possible. A broad `try` around `int()` conversion accidentally catches subsequent `raise ValueError(...)` calls, masking specific error messages.
- **Integrity Checks:** When creating test data, always verify `models.py` for `nullable=False` fields. Missing them causes confusing `NOT NULL constraint failed` errors.