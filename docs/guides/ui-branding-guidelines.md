# UI Branding & Styling Guidelines

**System**: ChoreSpec Gamification System
**Theme**: Modern, Premium, Glassmorphism, Dark UI

This document serves as the single source of truth for all CSS, component styling, and UI rules for ChoreSpec. Adhering to these guidelines ensures a consistent, high-quality user experience and prevents common regressions (like invisible text in dark mode).

---

## 1. Global Theming Strategy

ChoreSpec uses a **Forced Dark Theme**. We do not support a light mode toggle, nor do we respect the OS-level `prefers-color-scheme: light/dark` media queries. The application is designed to be immersive, glowing, and gamified.

### 🚫 Anti-Pattern: OS Color Scheme Queries
**Never** use `@media (prefers-color-scheme: dark)` in your CSS files. Since the app is globally dark, wrapping dark styles in this media query will cause them to fail if the user's OS is set to Light mode, resulting in unreadable white-on-white text.
- **Rule**: Apply dark mode colors (e.g., `#f0f0f0` for text) directly to the base CSS classes.

---

## 2. Color Palette & Typography

Always use CSS variables defined in `index.css` for consistency. Avoid hardcoding hex values unless it's a very specific, localized override.

### Gradients (Primary Visual Interest)
- `--primary-gradient`: Linear `#667eea` to `#764ba2` (Buttons, Headers)
- `--secondary-gradient`: Linear `#f093fb` to `#f5576c` (Secondary Actions)
- `--success-gradient`: Linear `#4facfe` to `#00f2fe` (Completion, Goals)
- `--warning-gradient`: Linear `#fa709a` to `#fee140` (Alerts)

### Backgrounds & Glassmorphism
- `--bg-dark`: `#0f0f23` (The universal base background color)
- `--bg-card`: `rgba(255, 255, 255, 0.05)` (Base for glass cards)
- **Glass Effect**: True glassmorphism requires `backdrop-filter: blur(10px)`.

### Typography
- **Font Family**: `Inter` (Google Fonts), fallback to system sans-serif.
- **Text Primary**: `--text-primary` (`#ffffff`)
- **Text Muted**: `--text-muted` (`rgba(255, 255, 255, 0.5)`) - Use for subtitles and metadata.

---

## 3. Component-Specific Rules

### 3.1 Form Inputs & Dropdowns (`<select>`)

Forms are the most common source of dark mode bugs because browsers heavily style `<input>`, `<textarea>`, and `<select>` elements with aggressive white defaults.

**The Rule**: You MUST explicitly style the background and text color of ALL form elements, including the inner `<option>` tags.

```css
/* CORRECT APPROACH */
.input-field, select, textarea {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #f0f0f0; /* Force light text */
}

/* CRITICAL: Explicitly style options for dark mode visibility */
select option {
    background: #0f0f23; /* Or your dark base color */
    color: #f0f0f0;
}
```

### 3.2 Modals & Overlays

Modals should feel like they are floating above the application.
- **Backdrop**: Use a dark, semi-transparent backdrop with a blur. (`background: rgba(0, 0, 0, 0.5); backdrop-filter: blur(4px);`)
- **Container**: The modal itself should use the `.glass-card` styling with a higher shadow (`var(--shadow-lg)`).
- **Z-Index**: Ensure modals have a `z-index` higher than the navbar/sidebar (e.g., `1000`).

### 3.3 Interactive Cards & Hover States

Gamification requires responsive, tactile UI elements. Cards must react to user intent.
- **Default State**: `.glass-card`
- **Hover State**: Elevate the card (`transform: translateY(-2px)`) and increase the shadow opacity. DO NOT change bounding box sizing on hover, as it causes layout shift jitter.

### 3.4 Disabled & Locked States

When an element (like a reward) is locked or unavailable:
- **Visuals**: Use `filter: grayscale(1)` and reduce `opacity` (e.g., `0.7`).
- **Interaction**: 
  - 🚫 **Anti-Pattern**: Do NOT use `pointer-events: none` on the parent container if you want child elements (like a "Locked" badge) to remain visible or if you want custom tooltips on hover.
  - **Correction**: Disable actions internally (e.g., hide the Redeem button) and change the cursor to `default` or `not-allowed`.

---

## 4. Animation & Motion

Keep animations subtle and purposeful (maximum 250ms-350ms duration).
- **Entry Animations**: Lists and cards should use the `.fade-in` animation (a slight upward translation + opacity fade) defined in `index.css`.
- **Status Indicators**: Use infinite pulsing animations (`transform: scale()`, box-shadow swelling) to draw attention to actionable states, such as a reward becoming affordable. But restrict these to primary actions to avoid overwhelming the user.

---

## Conclusion
Before committing any new UI component, always ask:
1. Did I hardcode a white background or black text?
2. Did I test the `<select>` dropdown options?
3. Did I use CSS variables instead of manual hex codes?
4. Is it wrapped in an OS media query? (If yes, remove it).
