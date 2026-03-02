# Project Learnings & Patterns

This file captures accumulated knowledge from development sessions. The Librarian agent appends to this file after each significant session to preserve institutional memory.

> **Note:** General-purpose patterns and conventions have been promoted to  
> `docs/guides/design-conventions.md` and the `.agent/rules/` files.  
> This file now contains **session-specific context** and **edge-case gotchas** only.

---

## 📅 2026-02-07: Documentation Reorganization

### Session Context
- Established "Master + Guides" documentation architecture
- Reorganized `.agent/workflows/` and `.antigravity/` prompting guides
- Discovered 8GB RAM IDE optimization (exclude `node_modules`, `venv`, cache from file watching)

### Gotchas
- SQLite database location is `chorespec_mvp.db` at project root
- Backend runs on port `8000`, frontend on port `5173`
- `// turbo-all` annotation in workflow files enables auto-run for all `run_command` steps

---

## 📅 2026-02-07: Task Import/Export & DOC_SYNC

### Session Context
- Using human-readable role names (e.g., "Child") in export/import JSON makes AI-generated task lists easier
- Import/Export Design: metadata (version, timestamp) + `skip_duplicates` flag

### Gotchas
- The backend port is `8000` (not `8001` as previously noted in some sessions)
- DOC_SYNC constraint added — now enforced in `pre-commit.md` step 7

---

## 📅 2026-02-08: Reward Hub Redemption Flow

### Session Context
- `Transaction` model with `type='REDEEM'` uses negative `awarded_points`
- SSE event `reward_redeemed` follows the existing naming pattern
- Goal auto-clear: redeeming current goal reward clears `current_goal_reward_id`

### Gotchas
- German translations require careful handling of special characters (ö, ü) in confirmation messages

---

## 📅 2026-02-08: Split Redemption Implementation

### Session Context
- Contribution model: list of `{user_id, points}` objects validates cleanly with Pydantic
- Preset allocations ("Split Evenly", "Max from Each") reduce friction

### Gotchas
- Pydantic structure mismatch: `{"contributions": [...]}` vs `[...]` causes 422 errors
- `Reward` model does not have an `icon` field — only in schemas

---

## 📅 2026-02-08: Transaction Styling & Stability

### Session Context
- "Reconnecting" loop was caused by hardcoded port 8001 in `FamilyDashboard.tsx`
- `from datetime import datetime` conflicts with `import datetime` — stick to one per file

### Gotchas
- Premium table styling: `.table-container` with overflow + soft shadows for mobile

---

## 📅 2026-02-08: DB Versioning & Auto-Migration

### Session Context
- `SQLAlchemy.create_all()` never adds columns to existing tables — insufficient for evolving schemas
- `MigrationManager` checking `db_version` in `system_settings` on startup is the primary migration pattern

### Gotchas
- TDZ Issues: function declarations must be before `useEffect` hooks that call them
- Idempotent SQL: `IF NOT EXISTS` for `ALTER TABLE` — *(now in design-conventions.md §6.2)*

---

## 📅 2026-02-09: Quota Intelligence & Spec Persistence

### Session Context
- Agents must self-report when their tier is insufficient for high-reasoning tasks
- Context is lost on session restart — LEARNINGS.md is the primary persistence mechanism

### Gotchas
- `spec.md` workflow recommends Gemini Pro/Claude for drafting

---

## 📅 2026-02-10: Analytics & Backend Debugging

### Session Context
- `User` model uses `nickname`, not `username` — common trip-up
- Zombie processes hold port 8000 — *(now enforced in pre-commit.md step 0)*
- Agents often verify "page load" but miss "empty data" — verify data elements, not containers

### Gotchas
- Agent vs. User environment: browser subagent success doesn't guarantee user success (CORS, localhost)

---

## 📅 2026-02-10: Automated Backups

### Session Context
- `AsyncIOScheduler` on startup, `apscheduler.start()` after adding jobs
- File timestamp manipulation (`touch -t`) for testing retention policies
- Sync/Async wrappers: standard `def` functions (not `async def`) for synchronous file ops in FastAPI

### Gotchas
- `replace_file_content` tool fails on large chunks — break into smaller logical blocks
- `get_db` dependency defined in `database.py`, localized import in `main.py` avoids circular refs
- `TaskInstance` relates to `User` via `user_id` — not `completed_by_user_id`

---

## 📅 2026-02-11: Import Wizard Fix (Localization & UX)

### Session Context
- Normalizing localized inputs ("täglich" → "daily") at Pydantic validator level
- "Weekly" tasks with specific time → interpret as "Recurring" with 7-day interval
- Role localization: German "Kind" must map to "Child" via `role_aliases`

### Gotchas
- Dark Mode CSS: error message containers need CSS variables or semi-transparent backgrounds

---

## 📅 2026-02-11: Unit Tests & Mobile Polish

### Session Context
- `PYTHONPATH=.` required for pytest from project root — *(now in qa-python.md)*
- Validation granularity: separate format check from logic check for helpful error messages

### Gotchas
- Broad `try/except ValueError` around `int()` catches explicit raises — *(now in qa-python.md)*

---

## 📅 2026-02-11: Timezone Support & Zombie Processes

### Session Context
- APScheduler defaults to system timezone (UTC in containers) — configure explicitly
- `scheduler.shutdown()` needs strict `try/except` to avoid zombie processes

### Gotchas
- Importing `backend.main` triggers `FastAPI()` init — mock side-effects before import in tests

---

## 📅 2026-02-12: Zombie Processes & Analytics Tests

### Session Context
- `scheduler.shutdown(wait=False)` prevents hangs during dev reload
- `nullable=False` fields cause confusing `NOT NULL` errors — *(now in qa-python.md)*

---

## 📅 2026-02-12: Test Coverage & Documentation Sync

### Session Context
- Retroactive testing debt halts progress — Exec = Code + Tests mandate
- Router testing requires `seeded_db` fixtures for FK constraints
- Empty response: `val in [None, ""]` is safer than `val is None`

### Gotchas
- Adding Pydantic required fields breaks existing tests — use `Optional[str] = None` for backward compat

---

## 📅 2026-02-13: Frontend Polish & Mobile Verification

### Session Context
- Full-screen overlay menu (hamburger) for mobile navigation
- TSC `no-unused-vars` and `react-hooks/exhaustive-deps` are top technical debt sources

### Gotchas
- Toast z-index: ensure `z-50` to appear above modals
- Mobile grid: `minmax(280px, 1fr)` for older devices

---

## 📅 2026-02-13: Notification System & UI Polish

### Session Context
- Absolute positioning for dropdowns: switch `right: 0` to `left: 0` near viewport edge
- `mousemove`/`mouseup` on `window` (not element) for drag-to-resize
- Sidebar resizing: min 200px / max 480px constraints

### Gotchas
- `eslint-disable-next-line @typescript-eslint/no-floating-promises` for fire-and-forget async in `useEffect`
- Browser subagent: text content selectors more robust than dynamic IDs

---

## 📅 2026-02-19: Agent Handoffs Standardization

### Session Context
- Structured 4-part handoff block (Status Summary, Artifacts, Next Role, Handoff Prompt)
- "Agent" = role-playing prompts within a single conversational context, not separate LLM instances

---

## 📅 2026-02-19: Gamification Polish & Test Assertions

### Session Context
- Streak bonuses: additive (+0.1/day, cap +0.5) avoids exponential point inflation
- BDD tests must account for daily streaks and manual overrides in point calculations

### Gotchas
- SQLite `DATE` fields: SQLAlchemy handles `datetime.date` mapping if configured correctly

---

## 📅 2026-02-20: Reward Hub UI Polish & Advanced CSS

### Session Context
- Glassmorphism: `backdrop-filter: blur()` + semi-transparent bg + glowing shadows
- Visual math in modals: show "Balance - Cost = Remaining" for transparency

### Gotchas
- `pointer-events: none` blocks hover effects — *(now in qa-react.md and design-conventions.md §2.3)*

---

## 📅 2026-02-21: State Machines & Boolean Coercion

### Session Context
- Separate `current_points` (spendable) and `lifetime_points` (XP) made penalties trivial
- `TransactionType` enum extended with `PENALTY` alongside `EARN` and `REDEEM`
- `IN_REVIEW` status in TaskInstance state machine instead of orthogonal boolean flags

### Gotchas
- Cross-layer boolean handling: normalize at boundary with `str(val).lower() in ('true', '1')`
- Optional fields missing in old JSON exports crash Pydantic — always define defaults

---

## 📅 2026-02-21: System Hardening & Docker Polish

### Session Context
- Non-root Docker: *(now in design-conventions.md §5.2)*
- `.dockerignore` critical for build performance
- Global empty state CSS in `index.css` prevents duplication

### Gotchas
- File permissions: `chown` writable directories before switching `USER`

---

## 📅 2026-02-21: Negative Points & State Separation

### Session Context
- Inline modal forms: modals over sub-routes for admin CRUD
- Centralized `api.ts` wrapper abstracts base URLs

### Gotchas
- `useState<number | ''>('')` for number inputs that can be cleared

---

## 📅 2026-02-21: Email Notifications & Background Tasks

### Session Context
- `BackgroundTasks` only execute after endpoint completes — cron needs manual execution
- Email dev fallback: dump payloads to terminal via `logger.info`
- Explicit `join(models.Target, condition)` over implicit joins

### Gotchas
- In-memory test DBs needed when adding columns — *(now in qa-python.md)*

---

## 📅 2026-02-22: Device Photo Upload & Multipart Forms

### Session Context
- HTML5 `capture="environment"` for native camera access
- `UploadFile` spools to disk; `StaticFiles` route for serving
- `URL.createObjectURL(file)` for client-side image preview

### Gotchas
- `file.content_type` and `file.filename` are `Optional[str]` — needs None checks for mypy
- Uploads require persistent Docker volume bind mount

---

## 📅 2026-02-22: Code Review Fixes — Boolean Columns & Orphan Cleanup

### Session Context
- `Column(Boolean)` with `.is_(True)` — *(now in design-conventions.md §6.3)*
- Nulling `reference_instance_id` preserves audit trail vs CASCADE deletion

### Gotchas
- `.update()` with Booleans needs `synchronize_session="fetch"` for `.in_()` queries
- Router refactoring: extract `EventBroadcaster` to `events.py` before splitting routes

---

## 📅 2026-02-23: Return-Type Annotations & Mypy Casts

### Session Context
- SQLAlchemy `Column[T]` to Pydantic typing: wrap in `str()`, `int()`, `bool()`
- `roles.get(Column[int])` causes mypy `[call-overload]` — cast lookup key

---

## 📅 2026-02-23: DRY Logic & Time-Travel Testing

### Session Context
- Deduplication: check `due_time >= start_of_day` regardless of status
- Shared `_generate_instances_for_task(db, task, today)` helper

### Gotchas
- Time-travel tests: shift both `completed_at` AND `due_time` backwards
- `db_session.commit()` required before subsequent API calls in BDD steps

---

## 📅 2026-02-23: Backend CRUD & Type Enforcement

### Session Context
- CORS: environment-driven definitions critical for containerized deployment
- FK safeties: explicit pre-delete NULLing for dynamic references

### Gotchas
- `RewardUpdate` with `Optional` fields + `model_dump(exclude_unset=True)` — *(now in design-conventions.md §3.2)*

---

## 📅 2026-02-23: Frontend React State & Deletion UX

### Session Context
- `window.confirm` fastest for destructive action prevention
- Form reuse with `formData` + `editingReward` state — *(now in qa-react.md)*

### Gotchas
- `window.location.reload()` is jarring — use `fetchData()` — *(now in qa-react.md and design-conventions.md §2.1)*

---

## 📅 2026-02-27: PIN Hashing & Passlib Troubleshooting

### Session Context
- `passlib` incompatible with `bcrypt>=4.1.0` — pin `bcrypt==4.0.1`
- SQLite locking: close Session before running raw `conn.execute()`
- Live DB migration via `v1_8_hash_pins.py` using `conn.execute(text(...))`

### Gotchas
- `typing.cast(str, ...)` needed for passlib returns in strict mypy

---

## 📅 2026-02-27: JWT Auth Middleware & Axios Interceptors

### Session Context
- FastAPI `Depends()` stacking for RBAC — *(now in design-conventions.md §3.4)*
- `app.dependency_overrides` for test auth fixtures
- Axios request interceptor for auto `Authorization: Bearer` injection
- Login returns `{ access_token, user }` — saves a roundtrip

### Gotchas
- 401 interceptor must exclude `/login` URL to prevent infinite redirect loops
- BDD tests: access `resp.json()["user"]["nickname"]` after auth transition

---

## 📅 2026-02-27: Web Push Notifications & Environment Loading

### Session Context
- Uvicorn `--env-file` requires `python-dotenv` installed
- VAPID public key must not be empty string — causes `InvalidAccessError`

### Gotchas
- Uncaught `PyJWTError` gives generic 401 — wrap with `logger.error`
- After changing password hashing strategy, run background migration immediately

---

## 📅 2026-02-28: Admin User Management (Edit & Delete)

### Session Context
- Deep deletion: explicitly delete `TaskInstance`, `Transaction`, `Notification`, `PushSubscription` before `User` — *(now in design-conventions.md §3.3)*
- Localized `setup_normal_user` fixture easier than rewriting global `conftest.py`

### Gotchas
- TSC duplicate definitions from careless merge — run lint before committing

---

## 📅 2026-03-02: Deletion Modal Dark-Mode Contrast Fix

### Session Context
- Modal white background + `var(--text-primary)` = invisible white-on-white text
- Hardcoded `#1a1a2e`, `#333`, `#c53030` — *(now in qa-react.md, design-conventions.md §1.1)*
- Self-deletion guard: `disabled` + tooltip — *(now in qa-react.md, design-conventions.md §2.3)*

### Gotchas
- Multiple iterations needed because `var(--text-secondary)` also resolves incorrectly in modals

---

## Template for Future Entries

```markdown
## 📅 YYYY-MM-DD: [Session Topic]

### Session Context
- [Key insight 1]
- [Key insight 2]

### Gotchas
- [Gotcha 1]
```
