# Security Review — Checklist

Detailed per-standard questions based on OWASP API Security Top 10.

---

## 1. Authentication & Authorization

| # | Check | What to Check in Code |
|---|-------|----------------------|
| S1 | Broken Object Level Authorization (BOLA) | When fetching/updating by ID (`/users/{id}`), does the code verify the resource actually belongs to the authenticated user? |
| S2 | Broken Authentication | Are JWTs properly validated (secret, expiration, alg)? Are passwords hashed securely (e.g. bcrypt)? Are secrets transmitted over plain HTTP? |
| S3 | Broken Function Level Authorization | Are administrative or privileged endpoints properly guarded by Role-Based Access Control (RBAC)? |

## 2. Resource Management & Filtering

| # | Check | What to Check in Code |
|---|-------|----------------------|
| R1 | Unrestricted Resource Consumption | Are endpoints protected by rate limiting? Are large queries paginated to prevent memory exhaustion/DoS? |
| R2 | Broken Object Property Level Authorization | Does the API prevent mass assignment? Are internal fields excluded from update schemas (e.g. preventing a user from updating `is_admin=True`)? Are returned objects filtered so sensitive fields are dropped? |

## 3. Input Validation & Injection

| # | Check | What to Check in Code |
|---|-------|----------------------|
| I1 | Injection | Are inputs passed to external systems safely? Specifically, is SQL injection prevented using parametrized queries or an ORM? Are command/exec calls avoiding user input? |
| I2 | Validation & Sanitization | Is all incoming data validated via strict typing (like Pydantic)? Are file uploads sanitized (MIME checks, safe filename generation)? |

## 4. Configuration & Headers

| # | Check | What to Check in Code |
|---|-------|----------------------|
| C1 | Security Misconfiguration | Is `DEBUG=True` disabled in production paths? Are CORS `allow_origins` reasonably restricted, or wildcard `*` improperly used? |
| C2 | Headers | Are standard security headers (HSTS, X-Content-Type-Options) implemented? |

## 5. DevSecOps & Secrets

| # | Check | What to Check in Code |
|---|-------|----------------------|
| D1 | Secrets in Code | Are there hardcoded API keys, DB passwords, or JWT secrets in the source code or `.env` templates? |
| D2 | Safe Dependencies | Does the project use dependency pinning? Were any obviously vulnerable libraries injected? |
| D3 | Server-Side Request Forgery (SSRF) | If the API makes outbound requests based on user input, is the URL strictly validated/allowlisted? |
