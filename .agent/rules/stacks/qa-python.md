---
trigger: glob
globs: **/*.py
---

# Python Testing Standards (Pytest)

- **Library:** Use `pytest` for all backend tests.
- **Fixtures:** Define shared fixtures in `conftest.py`. Do not duplicate setup code.
- **Mocking:** Prefer `unittest.mock.patch` as a decorator.
- **Async:** Use `pytest-asyncio` for async route testing.
- **Command:** Run tests using `pytest -v`.