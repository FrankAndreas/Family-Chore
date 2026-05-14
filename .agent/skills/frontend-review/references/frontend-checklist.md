# Frontend Review Standards Checklist

Evaluate the codebase against these core standards.

## 1. React Hook Best Practices
- **Rules of Hooks**: Are hooks called conditionally? Are they only called at the top level?
- **Dependency Arrays**: Are `useEffect`, `useMemo`, and `useCallback` dependency arrays exhaustive? Are there risks of stale closures?
- **Cleanup**: Do effects that set up subscriptions, timers, or DOM listeners have proper cleanup functions?

## 2. State Management & Data Flow
- **Local vs Global**: Is global state (Context/Redux/Zustand) overused for state that should be local to a component?
- **Prop Drilling**: Are props being passed down through too many layers? Could composition (`children`) or Context solve this better?
- **Derived State**: Is state being duplicated unnecessarily when it could be computed on the fly?

## 3. Component Architecture & Modularity
- **Separation of Concerns**: Are presentation components separated from container/logic components?
- **Reusability**: Are common UI elements (buttons, modals, inputs) extracted into reusable components, or duplicated?
- **File Structure**: Are related components, hooks, and styles grouped logically?

## 4. Performance & Re-renders
- **Memoization**: Are `React.memo`, `useMemo`, and `useCallback` used effectively to prevent expensive re-renders? Are they overused unnecessarily?
- **List Keys**: Do mapped lists use stable, unique `key` props (not array indices)?
- **Lazy Loading**: Are large route components or heavy libraries lazy-loaded using `React.lazy` and `Suspense`?

## 5. Styling Architecture
- **Consistency**: Are design tokens (colors, spacing, typography) used consistently, or are there hardcoded magic values?
- **Scoping**: Is CSS scoped correctly to prevent style leakage (via CSS modules, styled-components, or strict BEM)?

## 6. Error Handling & Fallbacks
- **Error Boundaries**: Are there React Error Boundaries catching rendering crashes gracefully?
- **Loading States**: Are there appropriate skeleton loaders or spinners for async operations?
- **Empty States**: Do lists and data views handle empty states gracefully?
