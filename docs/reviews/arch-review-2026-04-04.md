# Software Architecture Review — Family Chore Tracker

> **Reviewer**: Architecture Assessment  
> **Date**: 2026-04-04  
> **Scope**: Complete system (Frontend & Backend)

---

## Part 1: Standards Evaluated

| # | Standard | Description |
|---|----------|-------------|
| 1 | **Coupling & Cohesion** | Module independence and unified responsibilities |
| 2 | **SOLID Principles** | SRP, OCP, LSP, ISP, DIP evaluation |
| 3 | **Layering & Modularity** | Separation of concerns, bounded contexts, and dependency graphs |
| 4 | **Clean Architecture Boundaries** | Framework independence, persistence ignorance, DTOs |
| 5 | **Architectural Health** | Testability, error handling, logging, and cross-cutting concerns |

---

## Part 2: Findings by Standard

### 1. Coupling & Cohesion

| ID | Standard Check | Severity | Finding | File(s) |
|----|----------------|----------|---------|---------|
| AR1.1 | C1 High Cohesion | 🔴 | `crud.py` acts as a God object (900+ lines). It handles queries and mutations for Users, Tasks, Transactions, Rewards, Gamification, and Notifications in one massive file. | `backend/crud.py` |
| AR1.2 | C2 Low Coupling | 🟡 | Business logic directly creates related domain records. For instance, `redeem_reward` manages User points AND directly instantiates `models.Transaction` instead of delegating to a reporting/transaction module. | `backend/crud.py` |
| AR1.3 | C2 Low Coupling | 🟡 | Despite extracting sub-components, `FamilyDashboard.tsx` pulls the entire global state (Users, Tasks, Rewards, Transactions) into a single layer and orchestrates all API calls locally. | `frontend/src/components/FamilyDashboard.tsx` |

---

### 2. SOLID Principles

| ID | Standard Check | Severity | Finding | File(s) |
|----|----------------|----------|---------|---------|
| AR2.1 | S1 Single Responsibility | 🔴 | Gamification math (streaks, daily bonuses), backend business rules (awarding logic), and database persistence are entirely mixed in `_award_points_for_task`. | `backend/crud.py` |
| AR2.2 | S2 Open/Closed | 🟡 | Point multiplier and daily bonus logic is hardcoded inside functions. Extending gamification rules (e.g., weekend bonuses) requires modifying core persistence logic rather than injecting strategies. | `backend/crud.py` |

---

### 3. Layering & Modularity

| ID | Standard Check | Severity | Finding | File(s) |
|----|----------------|----------|---------|---------|
| AR3.1 | L1 Separation of Concerns| 🔴 | Missing Service/Domain boundary layer. Fastapi Routers invoke `crud` which directly manipulates SQLAlchemy models. The Database logic effectively acts as the Business Domain layer. | `backend/main.py`, `backend/routers/*.py` |
| AR3.2 | L3 Bounded Contexts | 🟡 | Lacks boundaries between disparate domains. Deleting a Task directly modifies Transactions to prevent constraint errors, signaling entanglement between the task definition domain and historical audit domains. | `backend/crud.py` |

---

### 4. Clean Architecture Boundaries

| ID | Standard Check | Severity | Finding | File(s) |
|----|----------------|----------|---------|---------|
| AR4.1 | B2 Persistence Ignorance | 🟡 | Application logic returns raw SQLAlchemy models which the framework dynamically parses. Business operations depend heavily on the ORM object structure. | `backend/routers/tasks.py` |
| AR4.2 | B1 Framework Independence| 🟢 | The frontend API interceptor relies on direct `window.location.reload()` to handle 401 exceptions, hard-coupling HTTP failure logic to a naive DOM reload instead of an application-state router response. | `frontend/src/api.ts` |

---

### 5. Architectural Health

| ID | Standard Check | Severity | Finding | File(s) |
|----|----------------|----------|---------|---------|
| AR5.1 | H1 Error Handling | 🔴 | Inconsistent backend error paradigms. Some functions raise `ValueError` (caught by routers to throw 400s), while others return dictionary payloads like `{"success": False, "error": "..."}`, fragmenting how routers handle HTTP error mapping. | `backend/crud.py` |
| AR5.2 | H3 Testability | 🟢 | Time-dependent logic globally relies upon `datetime.now(timezone.utc)`. No clock dependency injection exists, forcing global `freezegun` mocking for unit tests verifying streaks or cooldowns. | `backend/crud.py` |

---

## Part 3: Summary Scorecard

| Standard | Score | Key Notes |
|----------|-------|-----------|
| Coupling & Cohesion | ⭐⭐ | Heavy reliance on `crud.py` God object creates massive coupling. |
| SOLID Principles | ⭐⭐ | Gamification logic and CRUD operations violate SRP heavily. |
| Layering/Modularity | ⭐ | Absence of Service layer; domain logic resides exclusively inside database query structures. |
| Boundaries | ⭐⭐⭐ | Acceptable schema masking on API endpoints, but business logic uses direct ORM entities. |
| Architect Health | ⭐⭐ | Error handling lacks a uniform strategy. |

**Overall Architecture Maturity: ⭐⭐ (2.0/5)**

---

## Part 4: Top Priority Debts / Refactors

| Priority | IDs | Action |
|----------|-----|--------|
| 🥇 P0 | AR1.1, AR3.1 | Extract a standalone Service Layer to separate Business Logic from `crud.py`. Componentize into `services/tasks.py`, `services/gamification.py`, etc. |
| 🥈 P1 | AR5.1 | Standardize Error Handling: Define custom Domain Exceptions rather than mixing `ValueError` and dictionary returns. |
| 🥉 P2 | AR1.3 | Refactor `FamilyDashboard.tsx` to handle state through dedicated context providers or data-fetching hooks (e.g., React Query) rather than monolithic prop matching. |

---

## Tracking

- [ ] P0: Extract standalone Service Layer from `crud.py` (AR1.1, AR3.1)
- [ ] P1: Standardize Error Handling and Custom Domain Exceptions (AR5.1)
- [ ] P2: Modularize State handling in `FamilyDashboard.tsx` (AR1.3)
