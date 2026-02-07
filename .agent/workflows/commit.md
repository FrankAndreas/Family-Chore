---
description: Create clean, meaningful commits and push to remote
---

Use this workflow to stage changes intelligently and create descriptive commits.

---
**💡 Quota Recommendation**: Use **Gemini 3 Flash** for this workflow. Staging and committing are librarian/chore tasks.
---

// turbo-all

## 0. Choose Commit Mode

Before staging, decide on the commit granularity:

| Mode | When to Use | Example |
|------|-------------|---------|
| **Grouped** (default) | Multiple related files form one logical change | `docs: reorganize documentation structure` |
| **Atomic** | Each file/task should be independently revertable | Separate commits for each file changed |

**To use Atomic Mode**, say: "Use atomic commits" or "One commit per file".

---

## 1. Review Changed Files
Identify which files belong together for a logical commit.
```bash
git status
```

## 2. Stage and Commit

### Grouped Mode (Default)
I will group files by component (Backend, Frontend, Docs, CI) and create one commit per group.

### Atomic Mode
I will create one commit per file or per logical task. This is useful for:
- Bisecting bugs (`git bisect`)
- Reverting specific changes without affecting others
- Clear history for future AI sessions

**Example Commit Message Pattern (Conventional Commits):**
- `feat(component): add new feature`
- `fix(module): resolve bug in logic`
- `docs: update documentation`
- `chore: general maintenance`

## 3. Verify and Push
```bash
git log -n 5
git push
```

If using Atomic Mode, I will:
1. Stage each file individually.
2. Commit with a specific message for that change.
3. Repeat until all files are committed.
4. Push all commits once verification passes.
