# Security Audit Review — [Application / Scope]

> **Reviewer**: Security Assessment  
> **Date**: YYYY-MM-DD  
> **Scope**: [Complete system / specific scope]

---

## Part 1: Standards Evaluated (OWASP API Context)

| # | Standard | Description |
|---|----------|-------------|
| 1 | **Authentication & AuthZ** | BOLA, Auth integrity, Function-level access |
| 2 | **Resource Mgmt & Filtering**| Rate limits, mass assignment, data minimization |
| 3 | **Input Validation** | Injection prevention, Pydantic strictness |
| 4 | **Configuration & Headers**| CORS, debug modes, HTTP security headers |
| 5 | **DevSecOps & Secrets** | Secrets management, SSRF, dependency pinning |

---

## Part 2: Findings by Standard

### 1. Authentication & Authorization

| ID | Standard Check | Severity | Finding | File(s) |
|----|----------------|----------|---------|---------|
| SEC1| [e.g. BOLA]   | 🔴/🟡/🟢/✅ | [Description] | `file.py` |

---

### 2. Resource Management & Filtering
### 3. Input Validation
### 4. Configuration & Headers
### 5. DevSecOps & Secrets

---

## Part 3: Summary Scorecard

| Standard | Score | Key Notes |
|----------|-------|-----------|
| Authentication | ⭐⭐⭐ | [Notes] |
| Resource Mgmt | ⭐⭐⭐ | [Notes] |
| Validation | ⭐⭐⭐ | [Notes] |
| Configuration | ⭐⭐⭐ | [Notes] |
| DevSecOps | ⭐⭐⭐ | [Notes] |

**Overall Security Posture: ⭐⭐⭐ (X.X/5)**

---

## Part 4: Top Priority Fixes

| Priority | IDs | Action |
|----------|-----|--------|
| 🥇 P0 | [IDs] | [Action] |
| 🥈 P1 | [IDs] | [Action] |

---

## Tracking

- [ ] P0: [Action description] ([IDs])
- [ ] P1: [Action description] ([IDs])
