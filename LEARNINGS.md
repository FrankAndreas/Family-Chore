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
```
