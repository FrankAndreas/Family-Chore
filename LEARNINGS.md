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
