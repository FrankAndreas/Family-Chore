---
description: Create a feature specification before implementation
---

Use this workflow when starting a new feature. Run before any coding.

## 1. Describe the Feature
Tell me what you want to build in plain language.

## 2. I'll Generate a SPEC with:

### User Stories
```
As a [role], I want [feature] so that [benefit]
```

### Acceptance Criteria
```gherkin
Given [context]
When [action]
Then [expected result]
```

### Edge Cases
- What happens if X?
- What if the user does Y?
- Error handling for Z?

### Out of Scope
- What this feature does NOT include

## 3. You Confirm the SPEC
Review and approve, or request changes.

## 4. Integration
Once confirmed, I will:
1. Update **docs/master-spec.md** with any architectural changes.
2. Create a specific feature guide in **docs/guides/** if the feature is complex.

## 5. Then we PLAN → EXECUTE → VERIFY

---

**Example prompt:**
```
/spec

I want users to be able to set weekly allowance limits that reset every Sunday.
Parents can set limits, kids can see their remaining allowance.
```
