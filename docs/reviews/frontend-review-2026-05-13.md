# Software Architecture Review — Frontend React Core

> **Reviewer**: Frontend Assessment (LLM)  
> **Date**: 2026-05-13  
> **Scope**: Core Frontend Components (`App.tsx`, `FamilyDashboard.tsx`, `TaskForm.tsx`, `api.ts`)

---

## Part 1: Standards Evaluated

| # | Standard | Description |
|---|----------|-------------|
| 1 | **React Hook Best Practices** | Dependency arrays, Rules of Hooks, stale closures |
| 2 | **State Management & Data Flow** | Local vs Global state, Prop drilling, Derived state |
| 3 | **Component Architecture** | Separation of concerns, Reusability, Composition |
| 4 | **Performance & Re-renders** | Memoization, list keys, expensive computations |
| 5 | **Styling Architecture** | CSS scoping, token consistency, inline styles |
| 6 | **Error Handling & Fallbacks** | Boundaries, Loaders, Empty states, API fallbacks |

---

## Part 2: Findings by Standard

### 1. React Hook Best Practices

| ID | Severity | Finding | File(s) |
|----|----------|---------|---------|
| FE1 | 🟡 Medium | Linter rule disabled `eslint-disable-next-line react-hooks/exhaustive-deps` on the `activeTab` effect. `refreshTransactions` should be stabilized via `useCallback` (if it isn't already) and added to the array to prevent stale closures. | `FamilyDashboard.tsx:L57` |

### 2. State Management & Data Flow

| ID | Severity | Finding | File(s) |
|----|----------|---------|---------|
| FE2 | ✅ Good | Excellent pattern: Single form component externally controls state (`formData` passed as prop), enabling reuse for both Create and Edit operations in alignment with conventions. | `TaskForm.tsx` |
| FE3 | 🟡 Medium | Prop drilling of `currentUser` and `refreshUser` through multiple layout layers (`DashboardLayout`). Consider providing this via a `UserContext` to clean up the routing layer. | `App.tsx` |

### 3. Component Architecture & Modularity

| ID | Severity | Finding | File(s) |
|----|----------|---------|---------|
| FE4 | ✅ Good | Excellent decomposition. The core dashboard now successfully acts as a clean controller, delegating layout/render logic to modular sub-components (`TasksTab`, `RedeemTab`, `HistoryTab`). | `FamilyDashboard.tsx` |

### 4. Performance & Re-renders

| ID | Severity | Finding | File(s) |
|----|----------|---------|---------|
| FE5 | 🟡 Medium | `groupedTasks` and `unknownTasks` perform array reduction and filtering on every render. Because the component has frequent re-renders (e.g., from typing in the search bar/toasts), these calculations should be wrapped in `useMemo`. | `FamilyDashboard.tsx:L102` |

### 5. Styling Architecture

| ID | Severity | Finding | File(s) |
|----|----------|---------|---------|
| FE6 | 🟡 Medium | Excessive use of inline styles containing hardcoded magic colors (e.g., `color: '#ff4d4f'`, `background: 'linear-gradient(...)'`). Violates standard design token usage (`var(--error)`, etc) and prevents dark-mode overrides. | `TaskForm.tsx:L196` |

### 6. Error Handling & Fallbacks

| ID | Severity | Finding | File(s) |
|----|----------|---------|---------|
| FE7 | ✅ Good | Very clean handling of 401 Unauthorized via `registerForceLogout`, explicitly avoiding jarring `window.location.reload()` calls per project conventions. | `api.ts:L42` |
| FE8 | ✅ Good | Proper use of `<SkeletonLoader>` during loading states before data resolution. | `FamilyDashboard.tsx:L109` |

---

## Part 3: Summary Scorecard

| Standard | Score | Key Notes |
|----------|-------|-----------|
| Hooks | ⭐⭐⭐ | Generally solid, but disabling exhaustive-deps is a risk. |
| State/Data | ⭐⭐⭐⭐ | Great reuse of TaskForm. Minor prop drilling. |
| Architecture | ⭐⭐⭐⭐⭐ | Excellent decomposition of the FamilyDashboard. |
| Performance | ⭐⭐⭐ | Missing `useMemo` for derived heavy array operations. |
| Styling | ⭐⭐ | Significant technical debt with inline React styles overriding CSS. |
| Errors/Fallbacks | ⭐⭐⭐⭐⭐ | Perfect compliance with auth state and skeleton loaders. |

**Overall Frontend Maturity: ⭐⭐⭐⭐ (3.6/5)**

---

## Part 4: Top Priority Debts / Refactors

| Priority | IDs | Action |
|----------|-----|--------|
| 🥇 P1 | FE6 | **Remove Inline Styles**: Refactor `TaskForm.tsx` to move inline styling into a CSS module or use established CSS custom properties for error states. |
| 🥈 P2 | FE5 | **Memoize Derived State**: Wrap `groupedTasks` and `unknownTasks` calculations in `useMemo` in `FamilyDashboard.tsx` to prevent O(N) calculations on every keypress of the search term. |
| 🥉 P3 | FE1 | **Fix Dependency Array**: Remove the ESLint disable comment in `FamilyDashboard.tsx` and properly stabilize `refreshTransactions` using `useCallback`. |

---

## Tracking

- [x] P1: Remove Inline Styles in `TaskForm` (FE6)
- [x] P2: Memoize derived state in `FamilyDashboard` (FE5)
- [x] P3: Fix ESLint Hook Dependency (FE1)
