---
description: Run all quality checks before committing
---

Run these checks before git commit/push to catch CI failures early.

---
**💡 Quota Recommendation**: Use **Gemini 3 Flash** for this workflow. Running tests and linting are QA tasks.
---

// turbo-all

0. **Kill zombie processes** (prevents port conflicts)
```bash
fuser -k 8000/tcp 2>/dev/null || true
```

1. **Backend lint (flake8)**
```bash
cd /home/andreas/work/family-chore && ./venv/bin/python -m flake8 backend tests --max-line-length=120
```

2. **Backend type check (mypy)**
```bash
cd /home/andreas/work/family-chore && ./venv/bin/python -m mypy backend/
```

3. **Backend tests**
```bash
cd /home/andreas/work/family-chore && ./venv/bin/python -m pytest tests/ -v
```

4. **Frontend lint (ESLint)**
```bash
cd /home/andreas/work/family-chore/frontend && npm run lint
```

5. **Frontend type check (TypeScript)**
```bash
cd /home/andreas/work/family-chore/frontend && npx tsc --noEmit
```

6. **Frontend build test**
```bash
cd /home/andreas/work/family-chore/frontend && npm run build
```

7. **DOC_SYNC check**
Verify `docs/guides/user-guide.md` is up to date with any new user-facing features added in this session. Also review `docs/guides/design-conventions.md` for any new patterns discovered.

If all pass, safe to commit and push!
