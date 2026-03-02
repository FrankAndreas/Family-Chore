---
trigger: glob
globs: **/*.tsx
---

# React Testing Standards (Vitest / RTL)

- **Library:** Use `Vitest` + `React Testing Library`.
- **Selectors:** Prefer `screen.getByRole` (accessibility first) over `getByTestId`.
- **Snapshots:** Avoid snapshot testing for logic; use it only for purely visual components.
- **Browser Subagent:** For end-to-end flows, ask the user to open the Chrome Subagent instead of writing complex Cypress scripts.
- **Command:** Run tests using `npm run test`.

# React Component Conventions

- **Modal Text Colors:** NEVER use `var(--text-primary)` or `var(--text-secondary)` inside `.modal-content` — they resolve to white in dark mode on a white modal background. Use hardcoded dark colors: `#1a1a2e` for titles, `#333` for body text, `#c53030` for warnings.
- **State Refresh:** After CRUD operations (create/update/delete), call `fetchData()` to re-fetch and let React reconcile. NEVER use `window.location.reload()` — it's jarring and breaks CSS animations.
- **Self-Action Guards:** Use `disabled={entity.id === currentUser.id}` with `title="Cannot delete yourself"`. Do NOT use `pointer-events: none` (kills hover/tooltips) or hide the button entirely (confuses users).
- **Form Reuse:** Use a single form component with an `editing` state flag for Create/Edit modes. Share `formData` state + handlers to avoid duplication.
- **See also:** `docs/guides/design-conventions.md` for the full conventions reference.