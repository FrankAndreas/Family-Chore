---
description: Global project constraints and strict rules
globs: "**/*"
always_on: true
---
# Global Constraints

1. **STRICT_NO_DELETE**: Never delete blocks of code; comment them out or move to /temp/legacy.
2. **NO_BLIND_FIXES**: Never suggest a fix without first identifying the root cause in the terminal logs.
3. **SPEC_FIRST**: If a requirement is ambiguous, stop and ask the user before guessing.
4. **QUOTA_INTELLIGENCE**: If the current task does not match the Role's recommended model_tier, I MUST suggest an upshift (for quality) or downshift (to save quota). The user may explicitly overrule this (e.g., 'Stay on Pro for now').
5. **FRESH_CONTEXT**: For complex multi-step tasks, suggest chunking work into smaller units. After completing a major milestone (e.g., a full feature or 3+ file edits), remind the user: 'Consider committing and restarting the session for fresh context.' This prevents context rot and RAM buildup.
6. **DOC_SYNC**: After implementing any user-facing feature, update docs/guides/user-guide.md before marking the task complete.
7. **MIGRATION_REQUIRED**: Any schema change in backend/models.py MUST be accompanied by a new migration script in backend/migrations/ and a version bump in backend/migrations/manager.py.
