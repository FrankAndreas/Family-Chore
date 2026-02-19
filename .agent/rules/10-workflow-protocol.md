---
trigger: always_on
---

# Workflow Protocol: SPEC-PLAN-EXECUTE-VERIFY

Every feature must follow this lifecycle. Do not skip steps without user override.

## 0. PRE-FLIGHT (Self-Check)
- **Goal:** Ensure clean environment.
- **Action:**
  - Check for zombie processes (`fuser -k 8000/tcp`).
  - Verify `docs/guides/user-guide.md` is up to date with previous features.

## 1. SPEC (Product_Owner)
- **Goal:** Define acceptance criteria and BDD scenarios.
- **Output:** Update `docs/master-spec.md`.

## 2. PLAN (Architect)
- **Goal:** Validate technical approach and API Contract.
- **Requirement:** 
  - Create `PLAN.md`.
  - **Define Pydantic Schemas & API Responses FIRST.** (Prevents Frontend blocking).

## 3. EXECUTE (Executor)
- **Goal:** Implement the plan AND corresponding unit tests.
- **Constraint:** Code is incomplete without tests. Follow patterns in `PLAN.md`.
- **Mandatory Quality Checks (Run BEFORE asking for review):**
  - Backend: `flake8 backend tests --max-line-length=120`
  - Backend: `mypy backend/`
  - Frontend: `npm run lint` & `npx tsc --noEmit`

## 4. REVIEW (Code_Reviewer)
- **Action:** Analyze uncommitted changes (`git diff`). 
- **Goal:** Catch bugs and ensure no technical debt is added.
- **Verification:** Confirm linters pass. STRICTLY ENFORCE PEP8 (whitespace, imports).
- **Goal:** Catch bugs and ensure no technical debt is added.

## 5. VERIFY (QA_Nerd)
- **Goal:** Run full regression suite + manual edge case verification.
- **Output:** `QA_Report` artifact.

## 6. SYNC (Librarian)
- **Trigger:** End of session or after 3 commits.
- **Action:** Summarize changes into `STATE.md` and `LEARNINGS.md`, then commit them.

---

## Agent Handoffs Protocol
Every phase transition requires an explicit handoff to the next Role. The outgoing agent MUST provide the user with the following standard handoff block:

- **Handoff:** 
  - **Status Summary:** A concise 1-2 sentence summary of what was just completed.
  - **Artifacts:** Exact paths/links to the files updated in this step (e.g., `docs/master-spec.md`, `PLAN.md`).
  - **Next Role:** The specific agent role required next.
  - **Handoff Prompt:** The exact exact copy-pasteable prompt the user can use to invoke the next role (e.g., `> "As Architect, please review the new specs in docs/master-spec.md and update PLAN.md."`)