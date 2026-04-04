# UX Review — 12-Standard Checklist

Detailed per-standard questions to evaluate during a code-level UX audit.

---

## 1. Nielsen's 10 Usability Heuristics

| # | Heuristic | What to Check in Code |
|---|-----------|----------------------|
| H1 | Visibility of System Status | Loading spinners/skeletons for async ops? SSE/WS connection indicators? Progress bars for multi-step flows? |
| H2 | Match System ↔ Real World | Domain-appropriate labels (not DB column names)? Natural language in UI text? Proper date/number locale formatting? |
| H3 | User Control & Freedom | Undo/cancel for destructive actions? "Go back" always available? Confirm dialogs for irreversible ops? |
| H4 | Consistency & Standards | Single modal system? Uniform button styles? Consistent icon library? Same error pattern everywhere? |
| H5 | Error Prevention | Input validation before submit? Disabled buttons when form invalid? Constraints (min/max/pattern) on inputs? |
| H6 | Recognition over Recall | Breadcrumbs? Context-sensitive labels? Descriptive empty states? Tooltips on icon-only buttons? |
| H7 | Flexibility & Efficiency | Keyboard shortcuts? Bulk actions? Power-user workflows? Sensible defaults? |
| H8 | Aesthetic & Minimalist Design | Minimal visual noise? Progressive disclosure? Collapsible sections for dense data? |
| H9 | Error Recovery | Actionable error messages (not just "Something went wrong")? Retry options? Preserved form state on error? |
| H10 | Help & Documentation | Onboarding hints? Contextual help links? Accessible documentation? |

---

## 2. WCAG 2.1 AA Accessibility

| Criterion | What to Check |
|-----------|---------------|
| 1.1.1 Non-text Content | `alt` on images, `aria-hidden` on decorative elements |
| 1.3.1 Info & Relationships | Semantic HTML (`<nav>`, `<main>`, `<section>`), `role="dialog"` + `aria-modal` on modals |
| 1.4.3 Contrast (Min) | Text contrast ≥ 4.5:1, large text ≥ 3:1. Check CSS custom properties for muted/secondary text colors |
| 1.4.11 Non-text Contrast | UI component boundaries, focus indicators ≥ 3:1 against background |
| 2.1.1 Keyboard | All interactive elements reachable via Tab. Focus traps in modals. Escape to close overlays |
| 2.4.1 Bypass Blocks | Skip-link to main content |
| 2.4.7 Focus Visible | `:focus-visible` styles on all interactive elements. No `outline: none` without replacement |
| 4.1.2 Name/Role/Value | ARIA labels on custom widgets, `aria-expanded`, `aria-pressed` where applicable |

---

## 3. Responsive Web Design

| Check | Detail |
|-------|--------|
| Breakpoints | ≥3 breakpoints: mobile (~480px), tablet (~768–1024px), desktop (~1440px+) |
| Fluid layout | Flex/grid with relative units, no fixed pixel widths on containers |
| Images/media | `max-width: 100%`, responsive images or `srcset` |
| Touch targets | ≥44×44px on mobile (per WCAG 2.5.5) |
| Viewport meta | `<meta name="viewport" content="width=device-width, initial-scale=1">` |

---

## 4. Design System Consistency

| Check | Detail |
|-------|--------|
| Token usage | Colors, spacing, typography via CSS custom properties, not hardcoded values |
| Duplicate definitions | No duplicate utility classes or conflicting token scales |
| Inline styles | Minimal or zero inline styles — all styles via classes/tokens |
| Component reuse | Shared components (Modal, Button, Toast) used everywhere, no one-off duplicates |
| Naming conventions | Consistent BEM, utility, or CSS Modules approach — not mixed |

---

## 5. Information Architecture

| Check | Detail |
|-------|--------|
| URL ↔ Nav alignment | URL paths match visual navigation hierarchy |
| Logical grouping | Nav sections group related features (not misplaced items) |
| Route-based navigation | Key views are routes (browser back works), not state toggles |
| Search/filter | Discoverable content filtering where item counts are high |

---

## 6. Form Design (Wroblewski)

| Check | Detail |
|-------|--------|
| Validation timing | After first submit, or on change/blur after first interaction — NOT on initial blur |
| Error messaging | Inline, next to the field, specific ("Must be at least 8 characters" not "Invalid") |
| Input types | Correct `type`, `inputMode`, `min`/`max`/`pattern` attributes |
| Labels | Every input has a visible `<label>` or `aria-label` |
| Progressive disclosure | Complex forms broken into steps or sections |

---

## 7. Feedback & Error Handling

| Check | Detail |
|-------|--------|
| Toast/notification system | Single unified system, not component-local implementations |
| ARIA live regions | `role="alert"` or `aria-live` on notifications |
| Dismiss controls | Toast has close button or auto-dismisses with reasonable timeout |
| Contextual errors | Error messages include entity name and failure reason |
| Error boundaries | React ErrorBoundary with i18n support and multiple recovery actions |

---

## 8. Performance UX

| Check | Detail |
|-------|--------|
| Loading states | Skeleton loaders or spinners for all data-fetching views |
| Debouncing | Search/filter inputs debounced (200–500ms) |
| Pagination/virtualisation | Long lists paginated or virtualised |
| Optimistic updates | Where appropriate (toggles, likes, quick actions) |
| Bundle size | No enormous unused dependencies |

---

## 9. Internationalization (i18n)

| Check | Detail |
|-------|--------|
| Translation coverage | All user-visible strings use `t()` / translation keys |
| Pluralisation | `_one` / `_other` keys for counts |
| Locale formatting | Dates, numbers, currencies formatted per locale |
| RTL readiness | `direction: rtl` support or at minimum no hardcoded left/right |
| No string concatenation | Use interpolation `t('key', { name })` not `t('hello') + name` |

---

## 10. Component Architecture

| Check | Detail |
|-------|--------|
| File size | Components < 400 lines. Flag monoliths > 500 lines |
| Single Responsibility | One concern per component (no API calls + UI + business logic in one file) |
| Prop drilling | Max 2–3 levels. Beyond that, use context or composition |
| Cross-directory imports | No `import '../other-feature/Component.css'` — hidden coupling |

---

## 11. Visual Design Quality

| Check | Detail |
|-------|--------|
| Design tokens | Consistent color palette, typography scale, spacing scale |
| Aesthetic cohesion | Unified visual language (glassmorphism, flat, material — not mixed) |
| Hover/active states | Interactive elements have visible state changes |
| Dark/light mode | Consistent theme support if applicable |

---

## 12. Touch & Mobile UX

| Check | Detail |
|-------|--------|
| Touch targets | ≥44×44px for all tappable elements |
| Gestures | Swipe, pull-to-refresh where contextually expected |
| Touch vs mouse | Touch event handlers alongside mouse events (or pointer events) |
| Thumb zone | Primary actions in bottom/centre of mobile viewport |
| No hover-only features | All hover-revealed content also accessible on touch |
