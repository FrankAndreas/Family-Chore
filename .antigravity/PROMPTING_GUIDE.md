# Quick Reference: Agent Prompting Guide

## Agent Roles & Model Tiers

### 🏗️ Architect
**Recommended Tier:** High (Pro/Claude)  
**Use for:** Planning, API design, logic flow, docs/master-spec.md updates.
**Prompt prefix:** "As Architect..."

### ⚡ Executor
**Recommended Tier:** Mid/Low (Pro-low/Flash)  
**Use for:** Code implementation, refactoring, standard changes.
**Prompt prefix:** "As Executor..." or just describe the task.

### 🔍 QA_Nerd
**Recommended Tier:** Low (Flash)  
**Use for:** Testing, browser verification, bug hunting.
**Prompt prefix:** "As QA_Nerd..."

### 📚 Librarian
**Recommended Tier:** Low (Flash)  
**Use for:** Context management, STATE.md updates, summarization.
**Prompt prefix:** "As Librarian..."

### 📋 Product_Owner
**Recommended Tier:** High (Pro/Claude)  
**Use for:** Drafting specs, requirement gathering, and updating docs/master-spec.md.
**Prompt prefix:** "As Product_Owner..." or use `/spec`

### 🔬 Researcher
**Recommended Tier:** Mid (Flash/Pro-low)  
**Use for:** Analyzing open-source and closed-source docs to find prior art.
**Prompt prefix:** "As Researcher..."
**Behavior:** Plans search strategy, asks for confirmation, then executes. Say "Skip research" for simple features.

### 🔍 Code_Reviewer
**Recommended Tier:** High (Pro/Claude) - **different model than Executor**  
**Use for:** Reviewing uncommitted code like a PR reviewer.
**Prompt prefix:** "As Code_Reviewer..."
**Behavior:** Uses `git diff` to analyze changes and provide feedback.

---

## 💡 Quota Intelligence Protocol

I am now calibrated to monitor your quota usage.
1. **Model Check**: If you use a **High** model for a **Low** task (e.g., using Claude to update `STATE.md`), I will suggest a **Downshift** to Flash.
2. **Quality Check**: If you use a **Low** model for a **High** task (e.g., using Flash for complex API design), I will suggest an **Upshift** to Pro/Claude.
3. **Overrule**: You can always ignore these suggestions by saying "Stay on [model]" or "Overrule: I have plenty of credits."

---

## Workflow: SPEC-PLAN-EXECUTE-VERIFY

For any significant feature:

0. **SPEC** (Product_Owner - High Tier)
   "As Product_Owner, draft a spec for [feature]"

1. **RESEARCH** (Researcher - Mid Tier) *(optional)*
   "As Researcher, research how others implement [feature]"

2. **PLAN** (Architect - High Tier)
   "Plan the [feature] - what files, endpoints, and components are needed?"

3. **EXECUTE** (Executor - Mid/Low Tier)
   "Implement the plan" or "Implement [specific part]"

4. **REVIEW** (Code_Reviewer - High Tier, different model)
   "As Code_Reviewer, review the uncommitted changes."

5. **VERIFY** (QA_Nerd - Low Tier)
   "Verify [feature] works in browser" or "/pre-commit"

---

## 🔄 Agent Handoff Protocol

At the end of each session, I will suggest the next agent based on this flow:

| Current Role | Next Role | Suggested Prompt |
|--------------|-----------|------------------|
| Product_Owner | Researcher | "As Researcher, research how others implement this." |
| Researcher | Architect | "As Architect, plan the implementation." |
| Architect | Executor | "As Executor, implement the plan." |
| Executor | Code_Reviewer | "As Code_Reviewer, review the changes." |
| Code_Reviewer | QA_Nerd | "As QA_Nerd, verify the implementation." |
| QA_Nerd | Librarian | "As Librarian, update STATE.md and LEARNINGS.md." |
| Librarian | Fresh Session | Start new conversation: "What's my next step?" |

**To resume after a break**: Open a new conversation and say: **"What's my next step?"**  
I will read `STATE.md` and suggest the appropriate action.

## Quick Commands

| Command | What it does | Recommended Model |
|---------|--------------|-------------------|
| `/pre-commit` | Run all quality checks | Flash |
| `/spec` | Draft a feature specification | Pro/Claude |
| "Run tests" | Execute pytest | Flash |
| "Check in browser" | Browser verification | Flash |
| "Update STATE.md" | Librarian context sync | Flash |

## Global Constraints (from rules.json)

1. **STRICT_NO_DELETE** - Code is commented/moved, not deleted.
2. **NO_BLIND_FIXES** - Always identify root cause first.
3. **SPEC_FIRST** - Ask for clarification on ambiguous requirements.
4. **QUOTA_INTELLIGENCE** - Always verify model-task fit to save credits.
5. **FRESH_CONTEXT** - After major milestones, suggest committing and restarting for a clean session.
6. **MIGRATION_REQUIRED** - Schema changes must include a migration and version bump.
