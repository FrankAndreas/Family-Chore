---
description: Run all quality checks before committing
---

Run these checks before git commit/push to catch CI failures early:

// turbo-all

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

If all pass, safe to commit and push!
