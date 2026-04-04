# Backend Systems Review — Checklist

Detailed per-standard questions to evaluate during a backend code-level audit (focusing on FastAPI & Python).

---

## 1. FastAPI & Framework Usage

| # | Check | What to Check in Code |
|---|-------|----------------------|
| F1 | Dependency Injection (DI) | Are `Depends()` used correctly for DB sessions, user auth, and generic services? Are heavyweight initializations cached via DI? |
| F2 | Route Organization | Are routers (`APIRouter`) used to logically separate endpoints? Are tags and summaries utilized for documentation? |
| F3 | Exception Handling | Are `HTTPException`s raised with meaningful details? Is there a global exception handler to catch unhandled errors to avoid leaking stack traces? |
| F4 | Background Tasks | Are long-running, non-blocking tasks handed off to `BackgroundTasks` or message queues appropriately? |

## 2. Asynchronous Performance & Concurrency

| # | Check | What to Check in Code |
|---|-------|----------------------|
| A1 | Proper Async/Await | Are network-bound operations (DB queries, external API calls) using async/await properly? |
| A2 | Blocking the Event Loop | Are CPU-bound tasks or synchronous libraries illegally running inside `async def` route handlers? (They should be moved to a threadpool via `run_in_threadpool` or regular `def`). |
| A3 | Connection Pooling | Are database engines configured with appropriate connection pool limits and timeouts? |

## 3. Data Validation & Pydantic

| # | Check | What to Check in Code |
|---|-------|----------------------|
| P1 | Schema Separation | Are there distinct schemas for Create, Read, and Update operations to prevent over-posting or mass assignment? |
| P2 | Strict Validation | Are Field constraints (min_length, max_length, gt, lt, regex) used to validate data at the edges? |
| P3 | ORM Mode | Is `from_attributes=True` (formerly `orm_mode`) used properly on response schemas for easy serialization? |

## 4. Database Interaction (SQLAlchemy)

| # | Check | What to Check in Code |
|---|-------|----------------------|
| D1 | Session Management | Is the DB session yielded correctly via a dependency to avoid scope leaks? Is rollback handled on exceptions? |
| D2 | Query Efficiency | Are N+1 query problems avoided using `joinedload`, `selectinload` where appropriate? |
| D3 | Parameterized Queries | Are all queries using ORM methods or text() with parameters to prevent SQL injection? |
| D4 | Migrations | Are Alembic migrations tracked, and are schema modifications synchronized with models? |

## 5. Type Hinting & Code Quality

| # | Check | What to Check in Code |
|---|-------|----------------------|
| T1 | Strict Typing | Is the code using strict type hints everywhere (arguments, return types, Optional)? Does it pass `mypy` strict mode checks? |
| T2 | Linting Compliance | Does the code adhere to PEP8 guidelines / `flake8` max-line-length configurations? |
| T3 | Dead Code / Imports | Are there unused imports or unreachable code blocks? |

## 6. Testing & Maintainability

| # | Check | What to Check in Code |
|---|-------|----------------------|
| M1 | Unit & Integration Tests | Are endpoints covered by Pytest? |
| M2 | Mocking & DB Overrides | During tests, is the database dependency properly overridden with a test database? |
| M3 | Configuration Management | Are settings loaded via `pydantic-settings` from environment variables? Are secrets hardcoded? |
