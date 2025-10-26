# PRD: Bootstrap Frontend Implementation

## Introduction/Overview

The current AA Order Manager frontend lacks visual consistency and modern styling. This feature will implement Bootstrap 5 as the foundation for the UI, focusing on establishing a clean, consistent design system that improves visual coherence and development speed. The implementation will start with the Dashboard and Integration Management pages, creating reusable components for navigation and alerts that follow SOLID/DRY principles.

**Problem it solves:** Inconsistent styling across pages, slow frontend development, and lack of modern UI patterns.

**Goal:** Establish a Bootstrap-based design system with reusable components that ensures visual consistency and accelerates future frontend development.

## Goals

1. Implement Bootstrap 5 across Dashboard and Integration Management pages
2. Create reusable navigation and alert components following DRY principles
3. Implement dark mode support using Bootstrap's native capabilities
4. Ensure all pages follow consistent layout patterns
5. Maintain simple, clean code without heavy customization or animations
6. Optimize for desktop viewing experience

## User Stories

1. As a developer, I want a consistent component library so that I can quickly build new pages without reinventing styling.
2. As a user, I want a clean, modern interface so that the application feels professional and easy to navigate.
3. As a user, I want dark mode support so that I can choose my preferred viewing experience.
4. As a developer, I want reusable alert components so that I can display messages consistently across all pages.
5. As a staff user, I want clear navigation so that I can easily access Dashboard, Admin, and Integration Management pages.

## Functional Requirements

### Bootstrap Integration
1. The system must use Bootstrap 5 via CDN (no local installation required).
2. The system must use Bootstrap's default color scheme (no custom brand colors).
3. The system must implement Bootstrap's native dark mode support.
4. The system must NOT include custom animations or heavy Bootstrap customization.

### Base Template
5. The system must update `base.html` to include Bootstrap 5 CSS and JavaScript.
6. The system must include a consistent header/navigation component in `base.html`.
7. The system must include proper viewport meta tags for responsive behavior.
8. The system must provide a dark mode toggle accessible from all pages.

### Component Library
9. The system must create a `core/templates/components/` directory for reusable components.
10. The system must create a `_nav.html` component for consistent navigation across pages.
11. The system must create an `_alert.html` component for displaying system messages.
12. Components must follow Django's inclusion tag pattern for reusability.

### Navigation Component (`_nav.html`)
13. The navigation must display "AA Order Manager" as the site title.
14. The navigation must show the current username when logged in.
15. The navigation must provide links to Dashboard, Django Admin (staff only), and Manage Integrations (staff only).
16. The navigation must include a logout button/link.
17. The navigation must include a dark mode toggle switch.

### Alert Component (`_alert.html`)
18. The alert component must support Bootstrap's alert types (success, warning, danger, info).
19. The alert component must integrate with Django's messages framework.
20. The alert component must be dismissible.
21. The alert component must display integration status warnings consistently.

### Dashboard Page
22. The system must refactor `dashboard.html` to use Bootstrap grid system.
23. The dashboard must use Bootstrap cards for integration status display.
24. The dashboard must use Bootstrap button groups for admin/integration links.
25. The dashboard must follow consistent spacing using Bootstrap utility classes.

### Integration Management Pages
26. The system must refactor `integrations/manage.html` to use Bootstrap layout.
27. The system must refactor `integrations/index.html` to use Bootstrap layout.
28. Integration CTAs must use Bootstrap button styling.
29. Integration status displays must use Bootstrap badges/alerts.

### Layout Consistency
30. All pages must use `<div class="container mt-4">` as the main content wrapper.
31. All pages must use consistent heading hierarchy (h1 for page titles).
32. All pages must use consistent spacing utilities (mb-3, mt-4, etc.).

## Non-Goals (Out of Scope)

1. Form styling and validation patterns (deferred to future work)
2. Table components with sorting/filtering (deferred to future work)
3. Card components for data display (deferred to future work)
4. Mobile responsiveness optimization (desktop-focused for now)
5. Custom brand colors or logo integration
6. Complex JavaScript interactions or animations
7. Heavy customization of Bootstrap defaults
8. Order, Report, or Lease management pages (focus on Dashboard and Integrations only)

## Design Considerations

### Color Scheme
- Use Bootstrap 5 default colors:
  - Primary (blue): Action buttons, links
  - Success (green): Connected status, successful operations
  - Warning (yellow): Attention-needed states
  - Danger (red): Errors, disconnected status
  - Secondary (gray): Secondary actions

### Dark Mode Implementation
- Use Bootstrap 5's `data-bs-theme` attribute approach
- Store user preference in localStorage
- Provide toggle in navigation bar
- No custom dark mode styling beyond Bootstrap's defaults

### Spacing System
- Use Bootstrap spacing utilities consistently:
  - `mt-4`: Top margin for main content areas
  - `mb-3`: Bottom margin for sections/cards
  - `p-3`: Padding inside cards
  - `gap-2`, `gap-3`: For flex/grid spacing

### Typography
- Use Bootstrap's default typography scale
- Minimal custom CSS (< 50 lines for project-specific tweaks if needed)

## Technical Considerations

### Django Template Structure
- Maintain existing `base.html` inheritance pattern
- Use Django's `{% include %}` for components
- Consider creating template tags for complex components
- Keep existing context processors (integration_statuses, messages)

### File Organization
```
core/templates/
  components/
    _nav.html
    _alert.html
  core/
    base.html
    dashboard.html
integrations/templates/
  integrations/
    manage.html
    index.html
    _cta.html
static/
  css/
    custom.css  (minimal, < 50 lines)
  js/
    darkmode.js (simple toggle logic)
```

### Dependencies
- Bootstrap 5.3.2 via CDN (no npm/build process)
- No additional CSS frameworks or libraries
- Keep existing Django template dependencies

### Browser Support
- Modern desktop browsers (Chrome, Firefox, Safari, Edge)
- No IE11 support required

## Success Metrics

1. **Development Speed:** New pages can be created in < 30 minutes using component library
2. **Visual Consistency:** All Dashboard and Integration pages use consistent spacing, colors, and components
3. **Code Reusability:** Navigation and alerts use single-source components (no duplicated markup)
4. **Maintainability:** CSS customization < 50 lines total
5. **Functionality:** Dark mode toggle works across all pages with preference persistence

## Open Questions

1. Should the dark mode preference sync across devices/sessions? (Recommendation: localStorage only for now, defer server-side sync)
2. Should we create a style guide page for developers to reference components? (Recommendation: Add as follow-up task)
3. Do integration status badges need specific color coding beyond Bootstrap defaults? (Recommendation: Use Bootstrap semantics)

## Implementation Notes for Developer

### Getting Started
1. Start with `base.html` - add Bootstrap CDN links
2. Create `components/` directory and `_nav.html`
3. Update `dashboard.html` to use new structure
4. Test dark mode implementation
5. Apply same patterns to integration pages

### Testing Checklist
- [ ] Dark mode toggle persists across page navigation
- [ ] Django messages display as Bootstrap alerts
- [ ] Navigation links show/hide based on user permissions
- [ ] Integration CTAs display correctly in both light and dark modes
- [ ] No JavaScript console errors
- [ ] Pages render correctly at 1920x1080 and 1366x768 resolutions

### Existing Code to Preserve
- Integration status context processor
- Django messages framework integration
- Current user permission checks (is_staff)
- Integration CTA template tag logic

