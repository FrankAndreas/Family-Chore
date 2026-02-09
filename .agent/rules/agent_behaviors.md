---
description: Agent behaviors, workflows, and handoff protocols
globs: "**/*"
always_on: true
---
# Agent Behaviors

## Workflow Protocol: SPEC-PLAN-EXECUTE-VERIFY

For any significant feature:

1. **SPEC** (Product_Owner - High Tier)
   - Action: Define acceptance criteria, edge cases, and BDD scenarios before any technical planning. (Requires User confirmation)
   - Prompt: "As Product_Owner, draft a spec for [feature]"

2. **RESEARCH** (Researcher - Mid Tier) *(optional)*
   - Action: Analyze open-source and closed-source docs to find prior art.
   - Prompt: "As Researcher, research how others implement [feature]"

3. **PLAN** (Architect - High Tier)
   - Action: Validate technical approach before Executor writes code. (Requires PLAN.md)
   - Prompt: "Plan the [feature] - what files, endpoints, and components are needed?"

4. **EXECUTE** (Executor - Mid/Low Tier)
   - Action: Standard code implementation and modular refactoring.
   - Prompt: "Implement the plan" or "Implement [specific part]"

5. **REVIEW** (Code_Reviewer - High Tier, different model)
   - Action: Review uncommitted code like a PR reviewer.
   - Prompt: "As Code_Reviewer, review the uncommitted changes."

6. **VERIFY** (QA_Nerd - Low Tier)
   - Action: Verify fix in integrated browser or terminal. (Requires QA_Report)
   - Prompt: "Verify [feature] works in browser" or "/pre-commit"

7. **CONTEXT SYNC** (Librarian - Low Tier)
   - Action: Summarize recent changes into STATE.md to prevent context rot. (Frequency: After every 3 commits)
   - Prompt: "Update STATE.md"

## Agent Handoff

At the end of each session, suggest the next agent role based on this flow. State Field: `next_session_prompt`.

- **Product_Owner** -> **Researcher**: "As Researcher, research how others have implemented this feature." (Skip option: Say 'Skip research' for simple features to go directly to Architect.)
- **Researcher** -> **Architect**: "As Architect, plan the implementation based on the research findings."
- **Architect** -> **Executor**: "As Executor, implement the plan."
- **Executor** -> **Code_Reviewer**: "As Code_Reviewer, review the uncommitted changes." (Note: Use a DIFFERENT model than the one used for Executor.)
- **Code_Reviewer** -> **QA_Nerd**: "As QA_Nerd, verify the implementation."
- **QA_Nerd** -> **Librarian**: "As Librarian, update STATE.md and LEARNINGS.md."
- **Librarian** -> **Fresh Session**: Start a new conversation and ask: 'What's my next step?'
