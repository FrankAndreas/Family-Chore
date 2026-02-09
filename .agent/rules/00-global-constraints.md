---
trigger: always_on
---

# Global Project Constraints (Universal-GSD-Core)

1. **STRICT_NO_DELETE:** Never delete blocks of code. Comment them out or move them to `/temp/legacy`.
2. **NO_BLIND_FIXES:** Never suggest a fix without first identifying the root cause in the terminal logs.
3. **SPEC_FIRST:** If a requirement is ambiguous, stop and ask the user before guessing.
4. **MIGRATION_REQUIRED:** Any schema change in `backend/models.py` MUST be accompanied by a new migration script in `backend/migrations/` and a version bump.
5. **FRESH_CONTEXT:** If a session exceeds 3 file edits or complex debugging, suggest: "Consider committing and restarting the session for fresh context."
6. **DOC_SYNC:** After implementing any user-facing feature, update `docs/guides/user-guide.md` before marking the task complete.

## Quota Intelligence Protocol
- **Downshift:** If you are a High-Tier model (Claude/Pro) doing a low-value task (e.g., fixing typos), suggest switching to Flash.
- **Upshift:** If you are a Low-Tier model (Flash) struggling with logic, suggest switching to Pro/Claude.