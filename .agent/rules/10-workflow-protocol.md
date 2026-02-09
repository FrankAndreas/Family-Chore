---
trigger: always_on
---

# Workflow Protocol: SPEC-PLAN-EXECUTE-VERIFY

Every feature must follow this lifecycle. Do not skip steps without user override.

## 1. SPEC (Product_Owner)
- **Goal:** Define acceptance criteria and BDD scenarios.
- **Output:** Update `docs/master-spec.md`.

## 2. PLAN (Architect)
- **Goal:** Validate technical approach.
- **Requirement:** Create or update `PLAN.md` before any code is written.

## 3. EXECUTE (Executor)
- **Goal:** Implement the plan.
- **Constraint:** Follow the patterns defined in `PLAN.md`.

## 4. REVIEW (Code_Reviewer)
- **Action:** Analyze uncommitted changes (`git diff`).
- **Goal:** Catch bugs before they reach the repo.

## 5. VERIFY (QA_Nerd)
- **Goal:** Browser verification or terminal test pass.
- **Output:** `QA_Report` artifact.

## 6. SYNC (Librarian)
- **Trigger:** End of session or after 3 commits.
- **Action:** Summarize changes into `STATE.md` and `LEARNINGS.md`.