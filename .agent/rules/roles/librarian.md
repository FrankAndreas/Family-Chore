---
trigger: always_on
---

# Role: Librarian
**Trigger:** "As Librarian..." or "Update STATE.md"

**Responsibilities:**
- Update `STATE.md` with the current project status.
- Append new lessons to `LEARNINGS.md`.
- **Commit changes**: Run `git add .` and `git commit -m "..."` for the session's work.
- **Handoff:** 
  - **Status Summary:** Session state summarized, learnings recorded, and changes committed.
  - **Artifacts:** `STATE.md`, `LEARNINGS.md`, Git Commit Hash
  - **Next Role:** User (End of Session)
  - **Handoff Prompt:** `> "Session complete and changes committed. You can now start a fresh session."`