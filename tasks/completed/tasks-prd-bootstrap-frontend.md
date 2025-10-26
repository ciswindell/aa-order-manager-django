# Task List: Bootstrap Frontend Implementation

## Relevant Files

- `web/core/templates/core/base.html` - Main base template that all pages inherit from; updated with Bootstrap CDN links and component includes
- `web/core/templates/components/_nav.html` - Reusable navigation component with Bootstrap navbar, user info, permission-based links, dark mode toggle, and logout
- `web/core/templates/components/_alert.html` - Reusable alert component that maps Django messages to Bootstrap alerts with dismissible functionality
- `web/static/css/custom.css` - Minimal custom CSS file for project-specific styles
- `web/static/js/darkmode.js` - Dark mode toggle functionality with localStorage persistence for theme preference
- `web/core/templates/core/dashboard.html` - Dashboard page refactored with Bootstrap grid, cards, buttons, and alerts
- `web/integrations/templates/integrations/manage.html` - Integration management page refactored with Bootstrap cards, badges, and buttons
- `web/integrations/templates/integrations/index.html` - Integration index page refactored with Bootstrap grid and list groups
- `web/integrations/templates/integrations/_cta.html` - CTA partial updated with Bootstrap alert and button styling (removed inline styles)
- `web/core/tests/test_dashboard.py` - Existing tests that may need updates for new markup

### Notes

- Tests for Django templates typically verify context data and rendered content
- Use `python3 web/manage.py test core.tests.test_dashboard` to run dashboard tests
- Manual testing in browser required for visual verification and dark mode functionality

## Tasks

- [x] 1.0 Setup Bootstrap 5 and Base Template Infrastructure
  - [x] 1.1 Add Bootstrap 5.3.2 CSS CDN link to `<head>` in `base.html`
  - [x] 1.2 Add Bootstrap 5.3.2 JS bundle CDN link before `</body>` in `base.html`
  - [x] 1.3 Add viewport meta tag `<meta name="viewport" content="width=device-width, initial-scale=1.0">` to `base.html`
  - [x] 1.4 Create `web/static/css/` directory if it doesn't exist
  - [x] 1.5 Create `web/static/js/` directory if it doesn't exist
  - [x] 1.6 Create empty `web/static/css/custom.css` file for future project-specific styles
  - [x] 1.7 Update `base.html` main content area to use Bootstrap container: `<main class="container mt-4">`
  - [x] 1.8 Test that Bootstrap is loading by running dev server and inspecting page source

- [x] 2.0 Create Reusable Component Library (Navigation and Alerts)
  - [x] 2.1 Create directory `web/core/templates/components/`
  - [x] 2.2 Create `web/core/templates/components/_nav.html` with Bootstrap navbar structure
  - [x] 2.3 Add "AA Order Manager" branding to navbar
  - [x] 2.4 Add username display in navbar: "Welcome, {{ user.username }}"
  - [x] 2.5 Add navigation links (Dashboard, Django Admin, Manage Integrations) with Bootstrap nav styling
  - [x] 2.6 Add permission checks: show admin links only when `user.is_staff` is true
  - [x] 2.7 Add logout form/button to navbar using Bootstrap button styling
  - [x] 2.8 Add placeholder for dark mode toggle in navbar (implementation in task 3.0)
  - [x] 2.9 Include `_nav.html` component in `base.html` header section
  - [x] 2.10 Create `web/core/templates/components/_alert.html` for alert component
  - [x] 2.11 Implement alert component to map Django message tags to Bootstrap alert classes (success, warning, danger, info)
  - [x] 2.12 Add dismissible functionality to alert component using Bootstrap's dismiss button
  - [x] 2.13 Update messages block in `base.html` to use `{% include 'components/_alert.html' %}`
  - [x] 2.14 Test navigation links work correctly for staff and non-staff users
  - [x] 2.15 Test Django messages display as Bootstrap alerts

- [x] 3.0 Implement Dark Mode Support
  - [x] 3.1 Create `web/static/js/darkmode.js` file
  - [x] 3.2 Add dark mode toggle button/switch to `_nav.html` using Bootstrap form-check-switch
  - [x] 3.3 Implement JavaScript function to toggle `data-bs-theme` attribute on `<html>` element
  - [x] 3.4 Implement localStorage.getItem('theme') to load saved preference on page load
  - [x] 3.5 Implement localStorage.setItem('theme', value) to persist preference when toggled
  - [x] 3.6 Add event listener to dark mode toggle that calls theme switching function
  - [x] 3.7 Add initial theme detection script in `base.html` that runs before page render
  - [x] 3.8 Link `darkmode.js` in `base.html` before closing `</body>` tag
  - [x] 3.9 Test dark mode toggle switches theme and persists across page navigation
  - [x] 3.10 Test default theme (light) loads when no preference is stored

- [x] 4.0 Refactor Dashboard Page with Bootstrap
  - [x] 4.1 Update `dashboard.html` to remove existing inline styles
  - [x] 4.2 Wrap dashboard content in `<div class="row">` and `<div class="col-12">` structure
  - [x] 4.3 Update welcome heading to use `<h1 class="mb-3">Welcome, {{ user.username }}!</h1>`
  - [x] 4.4 Update admin links section to use Bootstrap button group: `<div class="btn-group">`
  - [x] 4.5 Style admin/integration links as Bootstrap buttons: `<a class="btn btn-outline-primary" href="...">`
  - [x] 4.6 Remove old `.admin-link` div wrapper and replace with Bootstrap utilities
  - [x] 4.7 Wrap integration CTA section in Bootstrap card: `<div class="card mb-3">`
  - [x] 4.8 Update Dropbox banner to use Bootstrap alert: `<div class="alert alert-warning">`
  - [x] 4.9 Update warning message to use Bootstrap alert: `<div class="alert alert-danger">`
  - [x] 4.10 Update logout form button to use Bootstrap styling: `<button class="btn btn-secondary">`
  - [x] 4.11 Apply consistent spacing utilities (`mt-3`, `mb-3`, etc.) throughout page
  - [x] 4.12 Test dashboard displays correctly in both light and dark modes
  - [x] 4.13 Verify existing dashboard tests still pass: `python3 web/manage.py test core.tests.test_dashboard`

- [x] 5.0 Refactor Integration Management Pages with Bootstrap
  - [x] 5.1 Update `integrations/manage.html` to extend `base.html` properly
  - [x] 5.2 Wrap manage.html content in Bootstrap grid: `<div class="row"><div class="col-12">`
  - [x] 5.3 Update page heading to use `<h1 class="mb-3">` in manage.html
  - [x] 5.4 Apply Bootstrap card structure to integration status sections in manage.html
  - [x] 5.5 Update integration connection status displays to use Bootstrap badges: `<span class="badge bg-success">`
  - [x] 5.6 Update `integrations/index.html` with Bootstrap grid structure
  - [x] 5.7 Apply consistent spacing utilities to index.html
  - [x] 5.8 Update `integrations/_cta.html` button styling to use Bootstrap classes: `<a class="btn btn-primary">`
  - [x] 5.9 Update integration CTA inline styles to use Bootstrap alert classes
  - [x] 5.10 Remove inline `style` attributes from _cta.html and replace with Bootstrap utility classes
  - [x] 5.11 Test integration OAuth flow still works correctly
  - [x] 5.12 Test integration status displays correctly in both light and dark modes
  - [x] 5.13 Run integration tests to verify functionality: `python3 web/manage.py test integrations.tests`

