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