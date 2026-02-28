# Project Learnings & Patterns

This file captures accumulated knowledge from development sessions. The Librarian agent appends to this file after each significant session to preserve institutional memory.

---

## 📅 2026-02-07: Documentation Reorganization

### What We Learned
- **Documentation Structure**: A "Master + Guides" architecture works well for both humans and AI agents. One master spec for "system truth" + separate guides for complex features.
- **Agent Calibration**: Workflow files (`.agent/workflows/`) and prompting guides (`.antigravity/`) must be updated together when file paths change.
- **IDE Optimization**: On 8GB RAM machines, excluding `node_modules`, `venv`, and cache directories from file watching is critical to prevent system freezes.

### Patterns Discovered
- **Quota Intelligence**: Mapping agent roles to model tiers (High/Mid/Low) helps users optimize credit spend.
- **YAML Frontmatter**: Workflow files require `description: ...` frontmatter to appear in the `/` slash command menu.

### Gotchas
- SQLite database location is `chorespec_mvp.db` at project root.
- Backend runs on port `8001`, frontend on port `5173`.
- The `// turbo-all` annotation in workflow files enables auto-run for all `run_command` steps.

---

## 📅 2026-02-07: Task Import/Export & DOC_SYNC

### What We Learned
- **Role Names > IDs for AI**: Using human-readable role names (e.g., "Child") in export/import JSON makes it easy for ChatGPT/Claude to generate valid task lists.
- **DOC_SYNC Constraint**: Adding a global constraint in `rules.json` ensures documentation updates aren't forgotten after features ship.
- **Browser Testing**: The `browser_subagent` tool is effective for verifying UI features end-to-end.

### Patterns Discovered
- **Import/Export Design**: Export with metadata (version, timestamp) + Import with `skip_duplicates` flag handles versioning and duplicate detection cleanly.
- **Modal Workflow**: Preview → Validate → Confirm pattern works well for bulk operations.

### Gotchas
- The backend port is `8000` (not `8001` as previously noted in some sessions).
- When adding new features, check `docs/guides/user-guide.md` — the new DOC_SYNC constraint will remind you.

---

## 📅 2026-02-08: Reward Hub Redemption Flow

### What We Learned
- **Transaction Modeling**: The existing `Transaction` model with `type='REDEEM'` was already designed for this use case. Redemptions use negative `awarded_points` to represent spending.
- **Confirmation Modals**: Users appreciate explicit confirmation before irreversible actions. The blur-backdrop + slide-up animation pattern creates a premium feel.
- **Browser Subagent for Verification**: Using `browser_subagent` to capture real UI recordings is invaluable for documentation and proof-of-work.

### Patterns Discovered
- **SSE Event Naming**: `reward_redeemed` follows the existing pattern (`task_completed`, etc.) for real-time updates.
- **Goal Auto-Clear**: When a user redeems their current goal reward, automatically clearing `current_goal_reward_id` provides good UX.

### Gotchas
- The `window.location.reload()` is a temporary fix for updating points after redemption. SSE should handle this, but refresh ensures consistency.
- German translations require careful handling of special characters (ö, ü) in confirmation messages.

---

## 📅 2026-02-08: Split Redemption Implementation

### What We Learned
- **Frontend State Management**: Handling complex multi-user input (split contributions) requires careful state initialization (e.g. `useState(() => Object.fromEntries...)`) to ensure all users have an initial value.
- **BDD Verification**: Writing BDD scenarios (`tests/features/split_redemption.feature`) *after* implementation is a good verification step but ideally should be done *before* (TDD style) to catch interface mismatches early (like the 422 error we faced).

### Patterns Discovered
- **Contribution Model**: Using a list of `{user_id, points}` objects validates well with Pydantic and maps cleanly to backend logic.
- **Preset Allocations**: "Split Evenly" and "Max from Each" are essential UX patterns for multi-party payments/redemptions to reduce friction.

### Gotchas
- **Pydantic Validation**: When using a Pydantic model as a request body, ensure the client sends the correct JSON structure (e.g. `{"contributions": [...]}` vs `[...]`) to avoid 422 errors.
- **Model Fields in Tests**: Be careful when creating test data; ensure model instantiation only uses existing fields (e.g., `Reward` does not have an `icon` field in `models.py`, though it might in schemas).

---

## 📅 2026-02-08: Transaction Styling & Stability

### What We Learned
- **Port Mismatches**: The "Reconnecting" loop on the frontend was caused by a hardcoded port 8001 in `FamilyDashboard.tsx`, while the backend runs on 8000. Always check `API_BASE` constants when debugging connectivity.
- **Python Imports**: `from datetime import datetime` creates a conflict if you also use `import datetime`. Best practice: stick to one style per file or alias imports.

### Patterns Discovered
- **Premium Table Styling**: wrapping tables in a `.table-container` with overflow handling and soft shadows creates a much better mobile experience and visual depth than raw tables.
- **Dark Mode Dropdowns**: Browser default styles for `<select>` often break in dark mode (white text on white bg). Explicitly styling `option { background-color: var(--bg-dark); }` is a necessary fix.

### Gotchas
- **Inline Styles**: They are quick but hard to override for themes (like Dark Mode). Moving to CSS classes immediately saved time when fixing the dropdown issue.

---

## 📅 2026-02-08: DB Versioning & Auto-Migration

### What We Learned
- **Auto-Migration Risk**: Relying on `SQLAlchemy.create_all()` is insufficient for evolving schemas in containerized environments (Docker/Synology). It never adds columns to existing tables.
- **Frontend Silent Failures**: API failures due to schema mismatches can look like "empty data" if handle incorrectly. Always distinguish between `data.length === 0` and `error`.
- **Migration Manager**: A lightweight `MigrationManager` checking a `db_version` in `system_settings` on startup is a powerful pattern for simple SQLite apps.

### Patterns Discovered
- **Retry Flow**: Providing a "Retry Loading" button in error states reduces friction when intermittent DB issues occur.
- **MIGRATION_REQUIRED**: Enforcing migrations in `rules.json` ensures future agents (including LLMs) don't forget schema updates.

### Gotchas
- **TDZ Issues**: Function declarations in React components should always be defined *before* the `useEffect` hooks that call them to avoid Temporal Dead Zone errors.
- **Idempotent SQL**: Using `TRY...EXCEPT` or `IF NOT EXISTS` for `ALTER TABLE` prevents crashes on partially migrated databases.

---

## 📅 2026-02-09: Quota Intelligence & Spec Persistence

### What We Learned
- **Quota Intelligence Failure**: Agents must self-report when their tier (Low/Flash) is insufficient for high-reasoning tasks like drafting specifications. Failure to check `.agent/rules/00-global-constraints.md` leads to suboptimal architectural planning.
- **Context Volatility**: Internal context is lost on session restart. Recording lesson-learned entries in `LEARNINGS.md` is the primary mechanism for preserving institutional memory across restarts.

### Patterns Discovered
- **Tier-Aware Planning**: Always check model tier against `00-global-constraints.md` before starting any `PLANNING` phase tasks.

### Gotchas
- The `spec.md` workflow explicitly recommends Gemini Pro/Claude for drafting; failing to follow this is a breach of project-defined "Quota Intelligence Protocol".

---

## Template for Future Entries

```markdown
## 📅 YYYY-MM-DD: [Session Topic]

### What We Learned
- [Key insight 1]
- [Key insight 2]

### Patterns Discovered
- [Pattern 1]: [Description]

### Gotchas
- [Gotcha 1]

---

## 📅 2026-02-10: Analytics & Backend Debugging

### What We Learned
- **Zombie Processes**: When `uvicorn` fails to shut down cleanly, it holds onto port 8000, causing `Address already in use` errors that mask the *actual* startup error (like an ImportError) in subsequent runs. Always check/kill processes (`fuser -k 8000/tcp`) if startup fails mysteriously.
- **Attribute Consistency**: The `User` model uses `nickname`, not `username`. This is a common trip-up when copying standard Auth logic.
- **Empty State Blindness**: Automated agents often verify "page load" but miss "empty data". ALWAYS verify that expected data elements (e.g., specific numbers, list items) are present in the DOM, not just the container components.
- **Agent vs. User Environment**: Just because it works in the agent's headless browser doesn't mean it works for the user (e.g., CORS issues on localhost). When possible, ask the user to verify critically or use `curl` from the user's terminal to mimic their environment.

---

## 📅 2026-02-10: Automated Backups

### What We Learned
- **APScheduler in FastAPI**: Integrating `AsyncIOScheduler` on `startup` event works well, but requires handling the event loop carefully. Using `apscheduler.start()` after adding jobs ensures they are registered.
- **File System Verification**: verifying file *creation* is easy, but verifying *deletion* (retention policy) requires simulating time. Touching a file's timestamp (`touch -t`) is a reliable way to test expiration logic without waiting days.

### Patterns Discovered
- **Sync/Async Wrappers**: When calling synchronous file operations (like `shutil.copy`) from an async FastAPI app, wrapping them in a standard `def` function (not `async def`) allows FastAPI to run them in a thread pool, preventing blocking of the main event loop.

### Gotchas
- **Large Edit Failures**: The agent tool `replace_file_content` fails if the target chunk is too large or has minor whitespace differences. Breaking large edits into smaller, logical blocks (e.g., Imports, Init, Startup) is much more reliable.


### Patterns Discovered
- **Dependency Injection**: The `get_db` dependency must be carefully managed to avoid circular imports. Defining it in `database.py` (and handling the localized import in `main.py`) is cleaner than circular refs between `main` and `database`.

### Gotchas
- **Relationship Fields**: `TaskInstance` relates to `User` via `user_id` (foreign key) and `user` (relationship). Attempting to access `completed_by_user_id` (a conceptual name) caused crashes. Always verify `models.py` definitions before waiting for a runtime error.

```

## 📅 2026-02-11: Import Wizard Fix (Localization & UX)

### What We Learned
- **Localized Inputs**: Users often input data in their native language (e.g., "täglich" instead of "daily"). Normalizing these inputs at the Pydantic validator level is a robust way to handle this without changing the core schema.
- **Implicit Intent**: Users may define "weekly" tasks with a specific time (e.g., "18:00"). While strict schemas might reject this, interpreting it as a "Recurring" task with a 7-day interval is a more user-friendly approach that preserves their intent.
- **Error Visibility**: Generic "Import failed" messages are frustrating. Exposing the underlying Pydantic/FastAPI validation errors (e.g., `loc` and `msg`) helps users self-correct their input especially when importing complex JSON.

### Patterns Discovered
- **Smart Schema Conversion**: Modifying the `schedule_type` on the fly within a validator (`@model_validator`) allows adapting user input to internal models seamlessly.

### Gotchas
- **Dark Mode CSS**: Error message containers with static background colors often become unreadable in dark mode. Using CSS variables (e.g., `var(--bg-error)`) or semi-transparent backgrounds ensures compatibility.
- **Test Dependencies**: When writing reproduction scripts, verify that the test runner (like `pytest`) is actually available in the environment before depending on it, or write standard Python scripts for portability.
- **Role Localization**: When importing data in a different language (e.g., German "Kind"), the backend MUST map these to system identifiers (e.g., "Child") or risk validation failures. Fixed by adding `role_aliases` in import logic.


## 📅 2026-02-11: Unit Tests & Mobile Polish

### What We Learned
- **Mobile Tables**: Standard HTML tables break mobile layouts. Wrapping them in a container with `overflow-x: auto` is mandatory for responsive design.
- **Pytest Module Resolution**: Running tests from the project root requires `PYTHONPATH=.` (or installing the package in editable mode) so that `backend.x` imports resolve correctly.

### Patterns Discovered
- **Validation Granularity**: When validating complex strings (like time formats), separate the *format check* (ValueError) from the *logic check* (range error) to give users helpful error messages instead of generic "invalid" errors.
- **CSS Utility Classes**: Creating a reusable `.table-container` class in `index.css` is cleaner than applying inline styles to every table component.

### Gotchas
- **Broad Exception Handling**: In `schemas.py`, a `try...except ValueError` block around `int()` conversion accidentally caught explicit `raise ValueError(...)` calls from subsequent logic, masking specific error messages. Always keep the try block scope as narrow as possible.

---

## 📅 2026-02-11: Timezone Support & Zombie Processes

### What We Learned
- **Scheduler Defaults**: `APScheduler` defaults to the system timezone (often UTC in containers). Explicitly configuring `scheduler.configure(timezone=...)` is required for localized cron triggers (e.g., midnight resets).
- **Shutdown Resilience**: `uvicorn` shutdown signals can be flaky with reloaders. Wrapping `scheduler.shutdown()` in a strict `try...except` block with logging ensures that one failed component doesn't hang the entire process, creating zombies.

### Patterns Discovered
- **Mock Verification**: When verifying environment-dependent logic (like timezones or database settings), mocking the dependency (e.g., `crud.get_system_setting`) in a dedicated script (`tests/verify_timezone.py`) allows proving the logic works without setting up a full database.

### Gotchas
- **Import Side Effects**: Importing `backend.main` often triggers `FastAPI()` initialization and database connections immediately. When writing test scripts, mock these side-effects *before* import using `sys.modules[...] = MagicMock()`.

## 📅 2026-02-12: Zombie Processes & Analytics Tests

### What We Learned
- **Scheduler Shutdown**: `scheduler.shutdown(wait=True)` is the default but causes `uvicorn` to hang if long-running jobs are active. Switching to `wait=False` ensures immediate shutdown, which is critical for development reload cycles and container restart policies.
- **Test Integrity**: When creating dummy data in tests, always check the `models.py` definitions for `nullable=False` fields (like `description` and `default_due_time`). Missing these causes `sqlite3.IntegrityError` which can be confusing if you only look at the error message "NOT NULL constraint failed".

### Patterns Discovered
- **Reproduction Scripts**: Writing a throwaway script (`tests/reproduce_hang.py`) to simulate the exact failure condition (e.g., a hanging job) is faster than trying to reproduce it via the full application.
- **Coverage-Driven Dev**: Identifying low-coverage modules (like `analytics.py`) and targeting them with specific unit tests is a high-ROI activity for stability.

## 📅 2026-02-12: Test Coverage & Documentation Sync

### What We Learned
- **Retroactive Testing Debt**: Building features without immediate tests leads to massive "Catch-Up" sessions that halt progress. The new `workflow-protocol.md` mandate (Exec = Code + Tests) is critical.
- **Router Testing Logic**: Testing API endpoints requires more than just `client.get`. You need `seeded_db` fixtures to ensure relations (like `role_id`) exist, otherwise foreign key constraints fail immediately.
- **Empty Response Handling**: API endpoints often return `None` as `null` in JSON, but sometimes as empty strings depending on the Pydantic serialization. Asserting `val in [None, ""]` is safer than `val is None`.

### Patterns Discovered
- **Contract-First**: Writing the Schema `class` before the React Component prevents the "Frontend Blocking" state where UI devs wait for API specs.
- **Doc-Sync Routine**: Checking `user-guide.md` during the "Pre-Flight" or "Review" phase prevents documentation drift. It's easier to update docs while the feature is fresh in memory.

### Gotchas
- **Pydantic Required Fields**: Adding a field like `description` to a Pydantic model (`TaskBase`) makes it required in all `POST/PUT` requests. This breaks existing tests that send partial data. Always use `Optional[str] = None` for backward compatibility or update all test payloads.

---

## 📅 2026-02-13: Frontend Polish & Mobile Verification

### What We Learned
- **Mobile Navigation**: A full-screen overlay menu (triggered by a hamburger icon) provides a much better experience on mobile than trying to squash a sidebar.
- **Visual Verification**: The `browser_subagent` is essential for verifying responsive layouts (e.g., iPhone X view) which are difficult to capture with standard integration tests.
- **Linting vs. Runtime**: TypeScript `no-unused-vars` and `react-hooks/exhaustive-deps` are the most common "technical debt" introduced during rapid prototyping. Fixing them *before* the "Verify" phase prevents late-stage regressions.

### Patterns Discovered
- **Global Feedback**: Implementing a generic `ToastContext` early saves significant time compared to ad-hoc `alert()` replacements later.
- **Error Boundaries**: Wrapping the entire `Routes` block in an `ErrorBoundary` is a safety net that should be standard in the project scaffold.

### Gotchas
- **Toast Z-Index**: Ensure `ToastContainer` has a high z-index (e.g., `z-50`) to appear above modals and sticky headers.
- **Mobile Grid**: When using `minmax(300px, 1fr)`, consider 280px for better support on narrower devices like older iPhones.

---

## 📅 2026-02-13: Notification System & UI Polish

### What We Learned
- **CSS Positioning**: Absolute positioning (`right: 0`) for dropdowns inside a relative container (`.notification-center`) works great until the container is near the right edge of the viewport. Switching to `left: 0` (or dynamic positioning) avoids clipping.
- **React Event Listeners**: For drag-to-resize features, attaching `mousemove` and `mouseup` to `window` (not the element) prevents the resize loop from breaking if the mouse moves faster than the element.

### Patterns Discovered
- **Floating Promises in Effects**: Validating `eslint` rules often flags async calls in `useEffect`. Using `// eslint-disable-next-line @typescript-eslint/no-floating-promises` is a pragmatic fix for fire-and-forget logic like `refreshNotifications()` where we don't want to complicate the effect with self-invoking async functions if error handling is internal.
- **Sidebar Resizing**: Using a `width` state controlled by mouse events gives users a sense of control ("customizable workspace"). Adding min/max constraints (200px/480px) prevents broken layouts.

### Gotchas
- **Browser Subagent Selectors**: When verifying UI, relying on text content (e.g. "Admin") is often more robust than trying to guess dynamic IDs or classes.

---

## 📅 2026-02-19: Agent Handoffs Standardization

### What We Learned
- **Context Preservation**: When handing off tasks between agents (roles), "position bias" can cause context loss. The handoff must include the minimum viable context needed for the next agent: a short status summary and exact paths to updated artifacts.
- **Agent Orchestration**: Handoffs in this system are procedural conventions (prompting shifts), not the spawning of isolated sub-agents (except for specific tools like `browser_subagent`). This relies heavily on the `Librarian` to record state before the context window fills up.

### Patterns Discovered
- **Structured Handoff Block**: A standardized 4-part handoff block (Status Summary, Artifacts, Next Role, Handoff Prompt) reduces cognitive load for the user and ensures the incoming agent has exactly what it needs to start.

### Gotchas
- **Sub-agent vs. Role**: It's easy to assume "Agent" means an entirely new LLM instance. Clarifying that these are role-playing prompts within a single conversational context is crucial for understanding how memory (and amnesia) works in this project.

---

## 📅 2026-02-19: Gamification Polish & Test Assertions

### What We Learned
- **BDD Point Scaling**: When applying global additive features (like a daily +5 bonus), BDD tests that assert exact mathematical points based solely on `base_points * multiplier` will fail. The baseline equation changes globally. Test coverage must account for daily streaks and manual overrides.
- **Frontend Streak Display**: Decoupling `current_streak` calculations from the raw transaction multiplier provides simpler UI presentation. We added a 🔥 streak badge and 🎁 daily bonus badge without cluttering the transactions table.

### Patterns Discovered
- **Additive Over Multiplicative**: Applying streak bonuses as additive values (base multiplier + 0.1 per day up to +0.5) is easier to track and cap than compounding percentages, avoiding exponential point inflation.

### Gotchas
- **Database Migrations and Dates**: Creating a simple `DATE` field in SQLite by adding a column via automated scripts requires checking strings if date matching fails, though SQLAlchemy handles `datetime.date` mapping gracefully if configured correctly.

---

## 📅 2026-02-20: Reward Hub UI Polish & Advanced CSS

### What We Learned
- **Dark Mode vs. OS Settings**: When an application forces a global dark theme regardless of the OS preference (`prefers-color-scheme`), applying dark-mode overrides via media queries creates inconsistencies. The CSS should simply apply the dark theme universally.
- **Glassmorphism Depth**: Using `backdrop-filter: blur()` combined with semi-transparent backgrounds and glowing box-shadows creates an immediate premium feel compared to flat colored cards.

### Patterns Discovered
- **Visual Math in Modals**: Explicitly showing the "Current Balance - Cost = Remaining Balance" inside the redemption confirmation modal builds user trust and transparency.
- **i18n Scaling**: Adding new UI components often means scattering new text strings. Using a structured namespace (e.g., `rewards.modal.*`) keeps translation files manageable.

### Gotchas
- **Pointer Events**: Setting `pointer-events: none` on an element (like a locked card) successfully blocks clicks but also kills hover effects. It's often better to leave events enabled and handle the "disabled" logic on the interactive elements inside (unless visually stripping the component is intended).

---

## 📅 2026-02-21: State Machines & Boolean Coercion

### What We Learned
- **Cross-Layer Boolean Handling**: Storing booleans as `Text` in SQLite (e.g. `'true'`, `'false'`, `'1'`, `'0'`) creates massive friction across the stack. Pydantic can often coerce these during parsing, but direct SQLAlchemy queries or backend logic that compares `if model.bool_field == "true"` will fail if Python evaluates `True` instead. Always normalize at the boundary: `str(val).lower() in ('true', '1')`.
- **Review Queues**: For features requiring asynchronous human approval (e.g. Photo Verification), adding an explicit `IN_REVIEW` status to the TaskInstance state machine is far cleaner than adding orthogonal boolean flags (`is_pending_review = True`), keeping the core status enum as the single source of truth for the instance lifecycle.

### Patterns Discovered
- **Progressive Enhancement of Endpoints**: Instead of rewriting the main `complete_task` endpoint to handle file uploads directly, adding a separate `upload-photo` endpoint that acts as a prerequisite keeps the main logic generic and handles file size/transfer constraints better.

### Gotchas
- **Import/Export Validation**: If an optional/default field was missing in earlier JSON exports (like `requires_photo_verification`), importing old JSON dumps will crash Pydantic if default values are not correctly defined in the `TaskImportItem` schema. Never assume exported data perfectly perfectly matches current schemas.
- **Data Privacy in APIs**: Moving sensitive or user-generated string inputs (like `photo_url`) from query parameters into the JSON request body prevents them from being logged in standard backend server logs (URL access logs).

---

## 📅 2026-02-21: System Hardening & Docker Polish

### What We Learned
- **Non-Root Execution**: Running Docker containers as non-root requires more than just a `USER` instruction. For Nginx, you must use an unprivileged base image (`nginxinc/nginx-unprivileged`) and switch from privileged ports (80) to unprivileged ones (8080).
- **Build Context Overhead**: Without `.dockerignore` files, sending large directories like `.git` or `node_modules` to the Docker daemon significantly slows down build times and clutters the image layers.
- **Global CSS Utility**: Standardizing empty state designs provides a premium feel across the app. Moving this to a global `index.css` prevents duplication in individual component CSS files.

### Patterns Discovered
- **Unprivileged Nginx**: Changing `listen 80;` to `listen 8080;` in `nginx.conf`, mapping `8080:8080` in `docker-compose.yml`, and using the `nginxinc` unprivileged image is a highly effective security pattern.
- **Consistent Empty States**: Using a combination of a semi-transparent dashed border block, an emoji icon, and clear "All caught up" messaging is a robust pattern for gamified systems to prevent dead-end screens.

### Gotchas
- **File Permissions**: When changing the container user (e.g., to `appuser` or `nginx`), you must explicitly `chown` the directories the app needs to write to or serve from before switching the `USER` instruction.

## 📅 2026-02-21: Negative Points & State Separation

### What We Learned
- **Separation of Balances**: Designing the system with separate `current_points` (spendable currency) and `lifetime_points` (XP/Tiers) early on made adding penalties trivial. We simply deduct from `current_points` without altering lifetime progression.
- **Enum Extensibility**: The `TransactionType` model was easily extended to support `PENALTY` alongside `EARN` and `REDEEM`, demonstrating that a single, unified transaction log is robust.

### Patterns Discovered
- **Inline Modal Forms**: When building management dashboards (like User Management), placing simple action modals inline with the iterator (e.g., clicking a user opens an overlay passing that user's state) is much faster to implement than dedicated sub-routes.
- **Centralized API Wrapper**: Using `api.ts` to construct `api.post` wrappers abstracts away base URLs and keeps React components clean.

### Gotchas
- **State Initialization**: In React, initializing a number input state to `''` instead of `0` or `undefined` can cause TypeScript union errors (`SetStateAction<number>`). Explicitly typing `useState<number | ''>('')` prevents coercion issues when the input is cleared by the user.

---

## 📅 2026-02-21: Email Notifications & Background Tasks

### What We Learned
- **FastAPI BackgroundTasks**: Using `BackgroundTasks` is an extremely lightweight and effective way to handle async operations like sending emails without blocking the HTTP response. However, they only execute *after* the endpoint completes, so if you are calling the logic from a cron job (outside a request context), you must pass a mock `BackgroundTasks` or handle execution manually.
- **Email Development Fallbacks**: In local dev environments without a configured SMTP server, dumping email payloads to the terminal via `logger.info` is a vital fallback to prevent crashes and allow QA verification.

### Patterns Discovered
- **Explicit Joins**: When writing complex SQLAlchemy queries involving multiple related tables (e.g., `User` -> `TaskInstance` -> `Task`), using explicit `join(models.Target, condition)` is significantly more reliable than implicit joins (`join(Target)`) which can sometimes yield ambiguous ORM issues or unexpected row multiplications.

### Gotchas
- **Test Database Migrations**: When adding new columns to models (like `email` to `User`), persistent unmigrated test databases will fail with `sqlite3.OperationalError` (missing column). Tests should prefer completely in-memory `sqlite:///:memory:` databases constructed cleanly via `Base.metadata.create_all` before every run to avoid state contamination.

## 📅 2026-02-22: Device Photo Upload & Multipart Forms

### What We Learned
- **Progressive Native Features**: The HTML5 `capture="environment"` attribute is a powerful, zero-dependency way to access a mobile device's camera natively. When combined with `<input type="file" accept="image/*">`, it seamlessly degrades to a file picker on desktops. This eliminates the need for complex PWA or Cordova wrappers for simple camera integration.
- **FastAPI Uploads**: `UploadFile` handles `multipart/form-data` efficiently by spooling large files to disk, preventing memory bloat. Serving these files back requires manually mounting a `StaticFiles` route (e.g., `/uploads`), which must be configured carefully to avoid directory traversal vulnerabilities and ensure the storage directory persists across restarts.

### Patterns Discovered
- **Form Data vs JSON**: Transitioning an endpoint from JSON to `multipart/form-data` requires abandoning standard Pydantic body definitions (`BaseModel`) for the specific endpoint arguments (`file: UploadFile = File(...)`) because `multipart` cannot mix seamlessly with JSON bodies without complex extraction logic.
- **Client-Side Blob Previews**: Using `URL.createObjectURL(file)` allows generating an immediate, lightweight preview of the selected image before it's uploaded to the server, greatly improving the user experience during verification.

### Gotchas
- **Mypy and UploadFile properties**: `file.content_type` and `file.filename` in FastAPI's `UploadFile` are typed as `Optional[str]`. Calling string methods (like `.startswith()` or `.split()`) without explicit `if file.filename:` None checks will fail strict mypy typing validations.
- **Docker Persistent Volumes**: By moving from URL strings to local file storage (`backend/uploads/`), we introduced stateful data into the container. Deployments must explicitly bind mount this directory, or all verification photos will 404 after a container restart.

---

## 📅 2026-02-22: Code Review Fixes — Boolean Columns & Orphan Cleanup

### What We Learned
- **SQLAlchemy `Boolean` on SQLite**: `Column(Boolean)` maps to `INTEGER` under the hood in SQLite, but SQLAlchemy handles Python `True`/`False` coercion properly. This eliminates fragile `== 1`/`== 0` comparisons and makes Pydantic schema alignment trivial (`bool` vs `int`).
- **Cascade Is Not Always the Answer**: For `delete_task` orphaning transactions, using `CASCADE` on the FK relationship would silently destroy audit records. Explicitly nulling `reference_instance_id` preserves transaction history while cleaning up the dangling reference — better for audit trails.
- **Scheduler Resilience**: Background scheduler loops that send emails must wrap each iteration in `try/except`. A single SMTP failure (bad address, timeout) would otherwise halt notifications for all remaining users in the loop.

### Patterns Discovered
- **`.is_(True)` over `== True`**: SQLAlchemy's `.is_(True)` and `.is_(False)` are the idiomatic way to query Boolean columns. Using `== True` triggers PEP8 E712 warnings and can behave unexpectedly with SQL NULL values.
- **Migration Validation**: For columns already stored as INTEGER but defined as `Column(Integer)`, switching to `Column(Boolean)` requires no data migration in SQLite — only a model/schema change. However, creating a validation migration script is good practice to document the intent and handle edge cases in other databases.

### Gotchas
- **Bulk `.update()` with Booleans**: SQLAlchemy's `.update({"read": True})` works correctly with Boolean columns, but you must use `synchronize_session="fetch"` (or `"evaluate"`) when combining `.filter().update()` using `.in_()` clauses, otherwise the session cache can become stale.


### A1: APIRouter Refactoring & Circular Imports
- When splitting a monolithic FastAPI app into routers, extract shared state (like `EventBroadcaster`) into a separate module (e.g. `events.py`) *before* extracting the routes. This prevents circular imports where routers need the broadcaster, but `main.py` needs the routers.
- Running Pytest against a project that was previously monolithic may require forcing `PYTHONPATH=.` so imports like `backend.database` resolve correctly outside of the app container.
- When creating pytest fixtures, avoid importing `app` and `get_db` together if it causes circular dependencies during load. Isolate the dependency overrides.

---

## 📅 2026-02-23: Return-Type Annotations & Mypy Casts

### What We Learned
- **SQLAlchemy to Pydantic Typing**: Pydantic schemas are usually flexible at runtime, but Mypy triggers errors when directly mapping SQLAlchemy `Column[T]` types to literal python types like `str` or `int` in manually constructed dictionaries or lists. 

### Patterns Discovered
- **Explicit Type Casting**: When extracting `Column` attributes to pass into strictly typed objects (like `TaskExportItem(name=...)`), wrapping the attributes in `str()`, `int()`, or `bool()` explicitly prevents Mypy `[arg-type]` errors and guarantees runtime stability.

### Gotchas
- **Mypy and Dictionary Lookups**: `roles.get(Column[int])` causes a Mypy `[call-overload]` error because it expects standard hashable primitives. We must look it up safely without casting the lookup key dynamically if Mypy doesn't understand the Column type resolution.

---

## 📅 2026-02-23: DRY Logic & Time-Travel Testing

### What We Learned
- **Deduplication vs. State**: Checking for duplicates during a daily reset based solely on `status == "PENDING"` is fragile. If a user completes a task early (STATUS -> COMPLETED) and the reset runs again, it spawns a duplicate. Checking only against `due_time >= start_of_day` regardless of status is much safer.
- **Time-Travel Testing**: When writing BDD tests that "advance time" by modifying a completed task's `completed_at` timestamp in the database, you must also shift the `due_time` (or creation time) backwards as well. Otherwise, stricter deduplication logic that filters on `due_time >= start_of_day` will see the task as belonging to *today*, creating contradictions.

### Patterns Discovered
- **Shared Helpers**: Extracting `_generate_instances_for_task` into a single function taking `(db, task, today)` ensures that ad-hoc task creation (`POST /tasks/`) and broad task creation (`POST /daily-reset/`) share the exact same cooldown, scheduling, and duplication rules.

### Gotchas
- **Pytest Side Effects**: Modifying timestamps directly in the database during Pytest BDD scenarios requires immediate `db_session.commit()` calls, otherwise subsequent API calls within the same test step won't see the shifted time context.

## 📅 2026-02-23: Backend CRUD & Type Enforcement

### What We Learned
- **CORS Best Practices**: Environment-driven CORS definitions are critical before moving from local dev to a containerized production environment across bridges/proxies.
- **Foreign Key Safeties**: Deleting items referenced dynamically (like a `Reward` referenced by a User's `current_goal_reward_id`) requires explicit pre-delete `NULL`ing across relationships to prevent constraint violations, as implicit CASCADE might behave unpredictably without strict DB migration coordination.

### Patterns Discovered
- **Progressive Typing**: Moving from `list[dict]` to strictly typed `list[SplitTransactionDetail]` payloads instantly guarantees frontend parsing stability, particularly when automated schema generators convert the OpenAPI JSON into TS interfaces.

### Gotchas
- **Pydantic Model Updates**: Adding partial update schemas (`RewardUpdate` where fields are `Optional`) simplifies Router logic directly because you can iterate over `.model_dump(exclude_unset=True)` effectively building an atomic SQLAlchemy patch update without manual null-checks.

## 📅 2026-02-23: Frontend React State & Deletion UX

### What We Learned
- **Destructive Action UX**: When a user clicks "Delete" on an item (like a Reward), the native `window.confirm` is the fastest, most reliable way to prevent accidental clicks before fetching to the backend.
- **Conditional Admin Rendering**: Complex state management for role-based UI (e.g., showing Edit buttons only if User is Admin) works securely only if the backend also matches the constraint. Our UI uses `currentUser.role.name === 'Admin'`, but the backend currently lacks that middleware constraint (noted in S2).

### Patterns Discovered
- **Form Reuse**: Reusing `formData` state alongside an `editingReward` state allows the same component to render a "Create" layout and an "Edit Modal" layout without duplicating handlers excessively, keeping the file lean.
- **Icon Buttons vs Text**: Using standard emojis (✏️, 🗑️) instead of full text buttons on cards keeps the UI uncluttered while still providing functionality, especially when paired with `title="Edit Reward"` for accessibility/tooltips.

### Gotchas
- **State Stagnation**: After a successful `update` or `delete`, `window.location.reload()` is a jarring UX. Simply calling `fetchRewards()` again and clearing the modal state (`setEditingReward(null)`) allows React to smoothly reconcile the DOM, preserving any CSS animations or current view state.

---

## 📅 2026-02-27: PIN Hashing & Passlib Troubleshooting

### What We Learned
- **Bcrypt Version Drift**: The `passlib` library has a known compatibility issue with `bcrypt>=4.1.0` (it relies on an old `__about__` attribute). To resolve this cleanly in legacy environments without dropping `passlib`, downgrade/pin `bcrypt==4.0.1`.
- **SQLite Locking During Migrations**: Attempting to execute `conn.execute()` updates using a SQLAlchemy raw `Connection` while the parent script holds an active `Session` bound to the same database file will cause `(sqlite3.OperationalError) database is locked`. The `Session` must update the settings inside the correct scope or the context manager must yield cleanly.

### Patterns Discovered
- **Type Casting SQLAlchemy Properties**: When applying strict typing (like `passlib` or custom models expecting Python primitives), SQLAlchemy declarative model objects (like `user.login_pin`) are seen by Mypy as `Column[str]` or `Any`. Wrapping these variables in `str()` explicitly satisfies type checkers without heavy schema alterations.
- **Live DB Migration Pattern**: We created an unmanaged custom migration script (`v1_8_hash_pins.py`) using `conn.execute(text("..."))` to fetch existing users, apply the new `bcrypt` hashing tool programmatically in python, and save back the hashed value seamlessly scaling over old plain text pins.

### Gotchas
- **Mypy and Passlib returns**: Functions from `CryptContext` like `.hash()` and `.verify()` are typed loosely or seen as `Any` by mypy strict mode. We added `typing.cast(str, ...)` to explicitly define their return contracts in `security.py`.

---

## 📅 2026-02-27: JWT Auth Middleware & Axios Interceptors

### What We Learned
- **FastAPI Dependency Injection**: `Depends()` is extremely powerful for RBAC. By stacking dependencies (`get_current_admin_user` calls `get_current_user` inside its own definition), we keep route signatures clean while ensuring 401s (Unauthenticated) and 403s (Forbidden) are handled beautifully.
- **Testing Dependency Overrides**: Re-writing large test suites for Auth can take days. FastAPI's `app.dependency_overrides` allows swapping out the `get_current_user` auth function entirely with a dummy fixture in `conftest.py`, instantly passing 95% of existing tests while still allowing targeted E2E checks on auth.
- **Axios Global Interceptors**: Handling global 401s via an Axios response interceptor (`api.interceptors.response.use`) is the cleanest way to clear expired local tokens and redirect to `/login` universally on the frontend without altering individual components.

### Patterns Discovered
- **Token Injection**: Attaching `Authorization: Bearer <token>` automatically in the frontend via an Axios *request interceptor* guarantees you don't forget to pass auth tokens to new API components.
- **Login Response Structure**: Rather than separating `/login` (which returns a token) and `/me` (which returns the user object), structuring `/login` to return `{ "access_token": "...", "user": { ... } }` saves a roundtrip and simplifies React Context initialization.

### Gotchas
- **Infinite Redirect Loops**: When setting up the 401 response interceptor, you MUST exclude the `/login` endpoint URL from triggering the logout action. Otherwise, an incorrect password attempt triggers a 401, which fires the interceptor, which drops state and reloads the page before the UI can show the error.
- **Type Aliasing for Verification**: In BDD tests, unpacking `resp.json()["nickname"]` will break immediately when transitioning from a direct User response to a structured Token response. Ensure all test coverage is updated to access `resp.json()["user"]["nickname"]` contextually.

## 📅 2026-02-27: Web Push Notifications & Environment Loading

### What We Learned
- **FastAPI Environment Variables**: Uvicorn's `--env-file` flag requires the `python-dotenv` package to be installed. Without it, the server crashes ungracefully when the flag is passed, or silently fails to load the variables if expected implicitly.
- **VAPID Key Handling**: Web Push API `subscribe()` fails instantly with `InvalidAccessError` (applicationServerKey is not valid) if the VAPID public key fetched from the backend is an empty string due to configuration misses.
- **PyJWT Silent Failures**: Uncaught `PyJWTError` exceptions in FastApi sub-dependencies (e.g. `jwt.decode`) will raise `401 Unauthorized` without context. Wrapping them with `logger.error` accelerates debugging when tokens fail unexpectedly.

### Patterns Discovered
- **Browser Subagent E2E Verification**: The `browser_subagent` handles popup permissions (like Web Push `Notification.requestPermission()`) extremely well when explicitly instructed to allow or run custom JS, making it great for testing browser APIs.

### Gotchas
- **Database Passwords Migration**: When changing the underlying Database password hashing strategy (like seeding plain text pins but shifting to bcrypt), explicit background migration (`python -c "update loop"`) is necessary instantly; otherwise, valid users lose access and get 500 server errors on the login endpoint due to `UnknownHashError`.
## Background Auto-Migration
- **Smooth Transitions**: Instead of forcing a hard migration script for something like plaintext passwords, intercepting the login flow to hash unencrypted secrets dynamically creates a zero-friction upgrade path for users while keeping the database clean moving forward.

## 📅 2026-02-28: Admin User Management (Edit & Delete)

### What We Learned
- **Deep Deletion Integrity**: When a user is deleted from a gamified ecosystem, standard SQLAlchemy `CASCADE` deletes are insufficient or risky. Explicitly querying and deleting related entities (`TaskInstance`, `Transaction`, `Notification`, `PushSubscription`) manually prior to the `User` record yields a much safer and auditable transaction loop.
- **Fixture Reusability**: When test suites define mock clients (like `admin_token` overriding `current_user`), it is frequently easier to create a localized `setup_normal_user` function inside a test file to explicitly spawn a secondary testing target than to rewrite the global `conftest.py` dependency overrides.

### Patterns Discovered
- **Inline Editor Modals**: Modals are preferred over separate pages for administrative CRUD interactions (like modifying Roles, points, or nicknames) because they maintain context of the underlying list without a jarring UX shift.
- **Role Inheritance Verification**: Combining frontend React conditional rendering (`if User is Admin show Edit`) with backend route dependencies (`@router.delete(..., dependencies=[Depends(get_current_admin_user)])`) is the primary pattern for securing admin routes. Providing fallback `403 Forbidden` handles tampering.

### Gotchas
- **TypeScript Duplicate Definitions**: Carelessly merging two separate `.tsx` or `.ts` file updates might accidentally re-declare variables (e.g. `updateUser`). Running `npm run lint` or `npx tsc --noEmit` locally before deployment validation prevents basic refactoring bugs from becoming production errors.
