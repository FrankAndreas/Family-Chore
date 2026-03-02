---
description: Create a feature specification before implementation
---

Use this workflow when starting a new feature. Run before any coding.

---
**💡 Quota Recommendation**: Use **Gemini 3 Pro** or **Claude** for this workflow. Drafting specifications requires high-tier reasoning.
---

## 1. Describe the Feature
Tell me what you want to build in plain language.

## 1.5. Check Existing Implementation
Before speccing from scratch, search the codebase for existing partial implementations:
- Check `backend/routers/`, `frontend/src/pages/`, and `models.py` for related code
- Review `docs/master-spec.md` for any prior mention of this feature
- If partial implementation exists, scope the spec to **complete** it rather than rebuild

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

## 2.5. Define API Contracts First
Before any route or frontend work begins:
- Define Pydantic request/response schemas in `backend/schemas.py`
- This prevents frontend blocking and ensures clear API contracts
- See `docs/guides/design-conventions.md` §3.1

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
