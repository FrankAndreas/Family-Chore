# Architecture Review — Checklist

Detailed per-standard questions to evaluate during a Software Architecture code-level audit.

---

## 1. Coupling & Cohesion

| # | Check | What to Check in Code |
|---|-------|----------------------|
| C1 | High Cohesion | Do modules/classes possess a single, unified purpose? Are unrelated functions lumped together into "Utils" or "Manager" God objects? |
| C2 | Low Coupling | How many external imports/dependencies does a core module have? Are internal implementation details accessed directly by other modules? |
| C3 | Logical Coupling | Are there hidden dependencies (e.g. implicitly shared global state or strict execution ordering) between modules? |

## 2. SOLID Principles

| # | Check | What to Check in Code |
|---|-------|----------------------|
| S1 | Single Responsibility | Does a class or file have only one reason to change? (e.g. separate parsing, validation, and storage) |
| S2 | Open/Closed | Can the existing behavior be extended via polymorphism or plugins without modifying the tested core logic? |
| S3 | Dependency Inversion | Do high-level business rules depend on abstractions rather than low-level concrete implementations? |
| S4 | Interface Segregation | Avoid "fat" interfaces requiring implementers to provide empty implementations for unused methods. |

## 3. Layering & Modularity

| # | Check | What to Check in Code |
|---|-------|----------------------|
| L1 | Separation of Concerns | Is there clear separation between UI, Business Logic, and Infrastructure/Persistence? |
| L2 | Arrow of Dependency | Do dependencies flow predominantly inward toward the domain logic? Are there circular dependencies? |
| L3 | Bounded Contexts | Are different business domains (e.g. Users vs Chores) separated logically and structurally to prevent monolithic entanglement? |

## 4. Clean Architecture & Boundaries

| # | Check | What to Check in Code |
|---|-------|----------------------|
| B1 | Framework Independence | Is core domain logic decoupled from specific frameworks (e.g. FastAPI/React)? Can it be unit tested purely using language native constructs? |
| B2 | Persistence Ignorance | Does the business logic possess awareness of ORM elements (like SQLAlchemy mapping classes directly used in presentation)? |
| B3 | Translation/DTO Layers | Are DTOs (Data Transfer Objects) and Mappers used to pass data across boundaries rather than leaking internal database models? |

## 5. Architectural Health & Cross-Cutting Concerns

| # | Check | What to Check in Code |
|---|-------|----------------------|
| H1 | Error Handling Strategy | Is error handling consistent across layers? Are unexpected internal errors swallowed, or bubbling up with generic context? |
| H2 | Observability/Logging | Do core actions log reliably for traceability without cluttering core logic? |
| H3 | Testability | Can modules be easily tested in isolation or does the setup require massive mocks/DB instantiations? |
