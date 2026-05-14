# Backend Review — ChoreSpec MVP

> **Reviewer**: Antigravity  
> **Date**: 2026-05-13  
> **Scope**: Complete Backend Codebase  
> **Framework**: FastAPI + SQLAlchemy

---

## Part 1: Standards Evaluated

| # | Standard | Description |
|---|----------|-------------|
| 1 | **FastAPI & Framework Usage** | Dependency injection, routing, exception handling, and background tasks |
| 2 | **Async & Performance** | Non-blocking execution, threadpool management, and connection handling |
| 3 | **Data Validation (Pydantic)** | Schema separation, strict validation, response models |
| 4 | **Database Interaction** | Session management, N+1 query prevention, parameterized queries |
| 5 | **Type Hinting & Quality** | Strict typing, PEP8 compliance, dead code elimination |
| 6 | **Testing & Maintainability** | Pytest coverage, dependency overrides, env var management |

---

## Part 2: Findings by Standard

### 1. FastAPI & Framework Usage

| ID | Standard Check | Severity | Finding | File(s) |
|----|----------------|----------|---------|---------|
| F1 | Dependency Injection (DI) | ✅ | Extensively and correctly uses `Depends()` for database sessions (`get_db`) and authentication logic (`get_current_user`, `get_current_admin_user`). | `routers/*.py`, `dependencies.py` |
| F2 | Route Organization | ✅ | Implements scalable router grouping (`APIRouter`) with distinct tags that are centrally aggregated in `main.py`. | `routers/*.py`, `main.py` |
| F3 | Exception Handling | ✅ | Global exception handler gracefully catches `DomainError` ensuring a standard error format, and `HTTPException`s are leveraged nicely. | `main.py`, `exceptions.py` |
| F4 | Background Tasks | 🟡 | `apscheduler` is used correctly for cron jobs. However, the `/backups/run` endpoint calls `run_backup_job()` directly synchronously instead of delegating to FastAPI's `BackgroundTasks`, blocking the request thread until the backup completes. | `main.py` |

---

### 2. Async & Performance

| ID | Standard Check | Severity | Finding | File(s) |
|----|----------------|----------|---------|---------|
| A1 | Proper Async/Await | ✅ | Endpoints are mostly declared as standard `def` when executing synchronous SQLAlchemy tasks, and `async def` when performing `await` tasks. | `routers/*.py` |
| A2 | Blocking the Event Loop | 🔴 | In `upload_task_photo`, a file chunk is read asynchronously but written synchronously (`buffer.write()`) in a `while` loop inside an `async def` route handler. This blocks the main event loop. Should use `aiofiles` or execute in a thread pool. | `routers/tasks.py` |
| A3 | Connection Pooling | 🟢 | Standard SQLite engine creation is used. Though appropriate for local/SQLite dev, production Postgres equivalents would require explicit connection pooling arguments (e.g. `pool_size`, `max_overflow`). | `database.py` |

---

### 3. Data Validation (Pydantic)

| ID | Standard Check | Severity | Finding | File(s) |
|----|----------------|----------|---------|---------|
| P1 | Schema Separation | ✅ | Excellent separation between Create, Read, Update schema structures (e.g., `TaskCreate`, `TaskUpdate`, `TaskBase`) preventing assignment loopholes. | `schemas.py` |
| P2 | Strict Validation | ✅ | Strong utilization of `Field()` constraints (`gt`, `le`, `pattern`, `min_length`, `max_length`) and `@model_validator` logic ensuring strict payload validation at the edges. | `schemas.py` |
| P3 | ORM Mode | ✅ | Standardized usage of `model_config = ConfigDict(from_attributes=True)` facilitating straightforward SQLAlchemy model serialization. | `schemas.py` |

---

### 4. Database Interaction

| ID | Standard Check | Severity | Finding | File(s) |
|----|----------------|----------|---------|---------|
| D1 | Session Management | ✅ | Secure `get_db` generator utilizing a `try/finally` block to safely commit or close DB sessions without leaking. | `database.py` |
| D2 | Query Efficiency | 🟡 | `crud.py` functions like `get_user_daily_tasks` return lists of models that serialize into nested Pydantic schemas (Task, User). Since they don't eagerly load relations using `options(joinedload(...))`, this triggers N+1 SQL queries during serialization. | `crud.py`, `models.py` |
| D3 | Parameterized Queries | ✅ | Complete reliance on SQLAlchemy ORM paradigms prevents raw SQL injection risks entirely. | `crud.py` |
| D4 | Migrations | ✅ | Application startup validates/applies Alembic migrations (`alembic_command.upgrade("head")`) gracefully. | `main.py`, `alembic.ini` |

---

### 5. Type Hinting & Quality

| ID | Standard Check | Severity | Finding | File(s) |
|----|----------------|----------|---------|---------|
| T1 | Strict Typing | ✅ | The entire backend passes `mypy --strict` flawlessly (0 errors across 35 source files). Strong explicit function type hinting. | Entire Codebase |
| T2 | Linting Compliance | ✅ | The entire backend passes `flake8 --max-line-length=120` flawlessly (0 errors). | Entire Codebase |
| T3 | Dead Code / Imports | ✅ | Clean imports detected with no unutilized code or dead logic paths spotted during analysis. | Entire Codebase |

---

### 6. Testing & Maintainability

| ID | Standard Check | Severity | Finding | File(s) |
|----|----------------|----------|---------|---------|
| M1 | Unit & Integration Tests | ✅ | Complete test suite relying cleanly on Pytest (`pytest-bdd`) ensuring good BDD functionality tracking. | `tests/` |
| M2 | Mocking & DB Overrides | ✅ | Flawless dependency overriding with an `sqlite:///:memory:` `StaticPool` during testing, avoiding file locking issues. | `tests/conftest.py` |
| M3 | Configuration Management | 🟢 | Employs raw `os.getenv(...)` variables scattered locally across multiple files. Utilizing `pydantic-settings` (`BaseSettings`) is heavily recommended for central parsing, typing, and validation of env variables. | `database.py`, `main.py` |

---

## Part 3: Summary Scorecard

| Standard | Score | Key Notes |
|----------|-------|-----------|
| FastAPI Usage | ⭐⭐⭐⭐ | Mostly solid, but backup route is unnecessarily blocking. |
| Async/Performance | ⭐⭐⭐ | Great usage of standard `def`, but one critical blocking disk write event in `async` router. |
| Data Validation | ⭐⭐⭐⭐⭐ | Exceptionally robust schemas and field validation rules. |
| DB Interaction | ⭐⭐⭐⭐ | Safely orchestrated, though plagued by unoptimized N+1 fetching on nested serialization. |
| Code Quality | ⭐⭐⭐⭐⭐ | Perfect `flake8` and `mypy` strict validations. Incredible quality. |
| Testing/Maintainability | ⭐⭐⭐⭐ | Perfect Pytest override strategies, lacks a robust Env Var config class. |

**Overall Backend Maturity: ⭐⭐⭐⭐ (4.2/5)**

---

## Part 4: Top Priority Fixes

| Priority | IDs | Action |
|----------|-----|--------|
| 🥇 P0 | A2 | Fix the event loop block in `routers/tasks.py::upload_task_photo`. Use `run_in_threadpool` or `aiofiles` for file writes. |
| 🥈 P1 | D2 | Apply `joinedload()` in `crud.py` functions returning nested entities (like `get_user_daily_tasks` with `models.TaskInstance`) to prevent N+1 queries. |
| 🥉 P2 | F4 | Convert `trigger_manual_backup` in `main.py` to accept `BackgroundTasks` and fire `run_backup_job()` into the background. |
| 🥉 P3 | M3 | Implement `pydantic-settings` to centralize environment variables instead of isolated `os.getenv` calls. |

---

## Tracking

- [x] P0: Fix blocking event loop in `upload_task_photo` (A2)
- [x] P1: Implement eager loading (`joinedload`) to fix N+1 queries in CRUD operations (D2)
- [x] P2: Refactor `/backups/run` to be non-blocking with `BackgroundTasks` (F4)
- [x] P3: Consolidate configuration management utilizing `pydantic-settings` (M3)
