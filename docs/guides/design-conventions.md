# Design & Engineering Conventions

**System**: ChoreSpec Gamification System
**Last Updated**: 2026-03-02

This document captures hard-won engineering rules distilled from 20+ development sessions. It complements `ui-branding-guidelines.md` (visual identity) with **how to build safely**.

> [!IMPORTANT]
> These are **mandatory conventions**, not suggestions. Every agent role must follow them.

---

## 1. CSS & Dark Mode

### 1.1 Modal Text Colors
Modals use `.modal-content` with a **white/light background** (`rgba(255, 255, 255, 0.95)`) that does NOT change in dark mode. Therefore:

- ❌ **NEVER** use `var(--text-primary)` or `var(--text-secondary)` inside modals — they resolve to white in dark mode → invisible text
- ✅ **ALWAYS** hardcode dark text colors inside modals:
  - Title text: `#1a1a2e`
  - Body text: `#333`
  - Warning/danger: `#c53030`

### 1.2 No OS Color Scheme Media Queries
(Also in `ui-branding-guidelines.md`)
- ❌ Never use `@media (prefers-color-scheme: dark)` — the app forces dark theme globally
- ✅ Apply dark styles directly to base CSS classes

### 1.3 Form Elements
- Always explicitly style `<select>`, `<option>`, `<input>` backgrounds
- Use `option { background: #0f0f23; color: #f0f0f0; }` to prevent white-on-white

### 1.4 Inline Styles vs CSS Classes
- Avoid inline styles for theming — CSS classes allow dark mode overrides
- Exception: one-off overrides inside modals (see 1.1) where class-based variables fail

---

## 2. React State & Component Patterns

### 2.1 State Refresh After CRUD
- ❌ Never use `window.location.reload()` — jarring UX, breaks CSS animations
- ✅ Call `fetchData()` and clear modal state (`setEditing(null)`)

### 2.2 Form Reuse
- Use a single form component with an `editing` state flag for both Create and Edit modes
- Share `formData` state + handlers across both modes to avoid duplication

### 2.3 Self-Action Guards
- ❌ Don't hide buttons entirely — it confuses users
- ❌ Don't use `pointer-events: none` — kills hover effects and tooltips
- ✅ Use `disabled={entity.id === currentUser.id}` with `title="Cannot delete yourself"`

### 2.4 State Typing
- Explicitly type mixed states: `useState<number | ''>()`
- Avoids TypeScript coercion errors when inputs are cleared

### 2.5 Confirmation for Destructive Actions
- Always show explicit confirmation modals for delete/deduct operations
- Show consequences clearly (e.g., "This will permanently remove...")

---

## 3. API & Backend Patterns

### 3.1 Schema-First Development
- ✅ Define Pydantic request/response schemas **before** writing routes or frontend
- This prevents frontend blocking and ensures API contracts are clear

### 3.2 Partial Updates
- Use `model_dump(exclude_unset=True)` for PATCH-style updates
- Create dedicated `*Update` schemas with all `Optional` fields

### 3.3 Deep Deletion
- ❌ Don't rely solely on SQLAlchemy `CASCADE` for audit-sensitive data
- ✅ Explicitly delete related records (`TaskInstance`, `Transaction`, `Notification`) before the parent entity
- This preserves audit trail control

### 3.4 Auth Stacking
- Use FastAPI `Depends()` chains: `get_current_admin_user` → `get_current_user`
- Both frontend conditional rendering AND backend route dependencies are required — never one without the other

### 3.5 Sensitive Data in Bodies
- ❌ Never put passwords, PINs, or user data in URL query parameters
- ✅ Use JSON request bodies — query params are logged in server access logs

---

## 4. Testing Conventions

### 4.1 Pre-Commit Checks (Mandatory)
Every commit must pass:
1. `flake8 backend tests --max-line-length=120`
2. `mypy backend/`
3. `pytest tests/ -v`
4. `npm run lint`
5. `npx tsc --noEmit`

### 4.2 In-Memory Test Databases
- ✅ Use `sqlite:///:memory:` with `Base.metadata.create_all()` for fresh test DBs
- ❌ Never depend on persistent test database files — stale schemas cause phantom failures

### 4.3 Narrow Exception Handling
- ❌ Don't wrap large blocks in `try/except` — swallows specific errors
- ✅ Keep try scopes minimal, catch only the expected exception type

### 4.4 Visual QA with Browser Subagent
- For any UI change involving modals, dark mode, or responsive layouts:
  - Use `browser_subagent` to capture screenshots
  - Verify text contrast and element visibility — linters can't catch visual bugs

### 4.5 Run with PYTHONPATH
- When running pytest from project root: `PYTHONPATH=. pytest tests/ -v`
- Required for `backend.*` imports to resolve correctly outside containers

---

## 5. Security Practices

### 5.1 Password/PIN Hashing
- ✅ Always use `bcrypt` via `passlib.CryptContext` — never store plaintext
- Auto-migration pattern: intercept login flow to silently rehash legacy plaintext credentials

### 5.2 Non-Root Docker
- Use `nginxinc/nginx-unprivileged` base image
- Listen on unprivileged ports (8080, not 80)
- Explicitly `chown` writable directories before `USER` instruction

### 5.3 Secrets Management
- JWT secret keys and VAPID keys: auto-generate at startup if missing
- Override via environment variables in production — never commit secrets

---

## 6. Database & Migrations

### 6.1 Migration Script Required
- Every schema change MUST have a corresponding migration script in `backend/migrations/`
- Bump the schema version in `system_settings`

### 6.2 Idempotent SQL
- Use `IF NOT EXISTS` or try-except for `ALTER TABLE` statements
- Prevents crashes on partially migrated databases

### 6.3 Boolean Columns
- ✅ Use SQLAlchemy `Column(Boolean)` with `.is_(True)` queries
- ❌ Never use `== True` (PEP8 E712) or `== 1` (fragile)

### 6.4 SQLite Locking
- Never hold an active `Session` while running raw `conn.execute()` on the same DB
- Close or commit sessions before running migration scripts

---

## 7. UX & Interaction Design

### 7.1 Empty States
- ❌ Never show a blank white page when data is empty
- ✅ Use dashed border + emoji + "All caught up" messaging

### 7.2 Toast over Alert
- ✅ Use `ToastContext` for feedback notifications
- ❌ Never use `window.alert()` — it blocks the UI thread

### 7.3 Modal Workflow
- Follow the **Preview → Validate → Confirm** pattern for bulk operations
- Show explicit mathematical breakdown for financial actions (e.g., "Balance - Cost = Remaining")

### 7.4 Mobile Responsiveness
- Tables: wrap in `.table-container` with `overflow-x: auto`
- Grids: use `minmax(280px, 1fr)` for older devices
- Navigation: use full-screen overlay menu on mobile, not compressed sidebar

---

## Quick Reference Checklist

Before committing any new UI component, ask:

- [ ] Did I use CSS variables inside a modal? (If yes, replace with hardcoded dark colors)
- [ ] Did I style `<select>` and `<option>` explicitly?
- [ ] Did I use `window.location.reload()`? (If yes, replace with `fetchData()`)
- [ ] Did I wrap in an OS media query? (If yes, remove it)
- [ ] Did I add a migration script for any schema change?
- [ ] Did I update `docs/guides/user-guide.md`?
