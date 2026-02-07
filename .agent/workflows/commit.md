---
description: Create clean, meaningful commits and push to remote
---

Use this workflow to stage changes intelligently and create descriptive commits.

// turbo-all

1. **Review Changed Files**
Identify which files belong together for a logical commit.
```bash
git status
```

2. **Stage and Commit Logical Groups**
Repeat this step for each logical group of changes. I will determine the grouping based on the files and your instructions.

**Example Commit Message Pattern (Conventional Commits):**
- `feat(component): add new feature`
- `fix(module): resolve bug in logic`
- `docs: update documentation`
- `chore: general maintenance`

3. **Verify and Push**
```bash
git log -n 5
git push
```

If you have many changes, I will:
1. Identify components (e.g., Backend, Frontend, CI, Docs).
2. Stage them separately.
3. Commit with a clear summary of "What" and "Why".
4. Push all commits once verification passes.
