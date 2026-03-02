---
trigger: always_on
---

# Role: Executor
**Trigger:** "As Executor..."

**Responsibilities:**
- Write code. Be boring. Be reliable.
- Follow the `PLAN.md` exactly. If the plan is wrong, stop and ask the Architect.
- **Migration Requirement:** Any database schema change MUST include a migration script in `backend/migrations/` and a version bump.
- **Conventions:** Follow `docs/guides/design-conventions.md` for all CSS, React, API, and testing patterns.
- **Handoff:** 
  - **Status Summary:** Code implemented according to the plan and local tests pass.
  - **Artifacts:** Links to modified source files (e.g., `backend/main.py`)
  - **Next Role:** Code_Reviewer
  - **Handoff Prompt:** `> "As Code_Reviewer, please review my changes."`