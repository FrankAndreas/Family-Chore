# Quick Reference: Agent Prompting Guide

## Agent Roles

### 🏗️ Architect (gemini-3-pro-high)
**Use for:** Planning, API design, logic flow, PLAN.md updates
**Prompt prefix:** "As Architect..."
```
Examples:
- "As Architect, design the notification system architecture"
- "As Architect, review and update PLAN.md for the rewards feature"
- "As Architect, what's the best approach for real-time sync?"
```

### ⚡ Executor (gemini-3-pro-low)
**Use for:** Code implementation, refactoring, standard changes
**Prompt prefix:** "As Executor..." or just describe the task
```
Examples:
- "Implement the notification service"
- "Add CRUD endpoints for rewards"
- "Refactor the task completion logic"
```

### 🔍 QA_Nerd (gemini-3-flash)
**Use for:** Testing, browser verification, bug hunting
**Prompt prefix:** "As QA_Nerd..."
```
Examples:
- "As QA_Nerd, verify the login flow works in browser"
- "As QA_Nerd, run all tests and fix failures"
- "As QA_Nerd, find the root cause of this error: [paste error]"
```

### 📚 Librarian (gemini-3-flash)
**Use for:** Context management, STATE.md updates, summarization
**Prompt prefix:** "As Librarian..."
```
Examples:
- "As Librarian, update STATE.md with today's changes"
- "As Librarian, summarize what we've done this session"
- "As Librarian, what's the current state of the project?"
```

## Workflow: PLAN-EXECUTE-VERIFY

For any significant feature:

1. **PLAN** (Architect)
   "Plan the [feature] - what files, endpoints, and components are needed?"

2. **EXECUTE** (Executor)
   "Implement the plan" or "Implement [specific part]"

3. **VERIFY** (QA_Nerd)
   "Verify [feature] works in browser" or "/pre-commit"

## Quick Commands

| Command | What it does |
|---------|--------------|
| `/pre-commit` | Run all quality checks |
| "Run tests" | Execute pytest |
| "Check in browser" | Browser verification |
| "Update STATE.md" | Librarian context sync |

## Global Constraints (from rules.json)

1. **STRICT_NO_DELETE** - Code is commented/moved, not deleted
2. **NO_BLIND_FIXES** - Always identify root cause first
3. **SPEC_FIRST** - Ask for clarification on ambiguous requirements
4. **QUOTA_SAFETY** - Use Flash model for repetitive tasks
