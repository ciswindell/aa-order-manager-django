# PRD: GUI Logic Extraction from app.py

## Introduction/Overview

Currently, `app.py` contains both business logic and GUI implementation tightly coupled together in a 459-line file. This creates maintenance challenges and makes it difficult to modify the GUI independently from the core application logic. This feature will extract all GUI components into a separate module, improving code organization and preparing for potential future GUI framework changes.

## Goals

1. **Improve Code Maintainability:** Separate GUI concerns from business logic for easier maintenance
2. **Enable Future GUI Framework Migration:** Create a clean separation that allows switching to different GUI frameworks
3. **Reduce app.py Complexity:** Significantly reduce the main file size by moving GUI code to dedicated modules
4. **Maintain Existing Functionality:** Preserve all current GUI behavior and user experience exactly as-is
5. **Follow SOLID/DRY Principles:** Apply clean code principles without overengineering - keep it simple and focused

## User Stories

- **As a developer**, I want to modify GUI layout without touching business logic so that I can make UI changes safely
- **As a developer**, I want to switch to a different GUI framework in the future so that I can modernize the interface without rewriting business logic
- **As a developer**, I want the main app.py file to be focused on coordination rather than GUI details so that I can understand the application flow quickly

## Functional Requirements

1. **Extract Main Window Creation:** Move all tkinter widget creation code (lines 294-458) to a separate GUI module
2. **Extract Progress Window:** Move the ProgressWindow class to the GUI module
3. **Create GUI Module Structure:** Establish `src/gui/` directory with appropriate module organization
4. **Maintain Data Flow:** Ensure GUI can still access and update form data without breaking existing functionality
5. **Preserve Event Handling:** Keep all button clicks, form submissions, and user interactions working exactly as before
6. **Extract Helper Functions:** Move GUI-related utility functions like `browse_file()` to the GUI module
7. **Reduce app.py Size:** Target reducing app.py from 459 lines to approximately 150 lines
8. **Maintain Import Structure:** Ensure the refactored code doesn't introduce circular imports or dependency issues

## Non-Goals (Out of Scope)

- Form validation logic (stays in app.py)
- Data binding or form state management (stays in app.py)
- Business logic extraction (only GUI components)
- Changing the GUI framework (tkinter remains)
- Modifying existing GUI behavior or appearance
- Creating reusable GUI components (just organizing existing code)
- Error handling logic (stays with business logic)
- Overengineering with unnecessary design patterns or abstractions
- Complex class hierarchies or interfaces - keep it simple

## Design Considerations

- **Module Structure:** Create `src/gui/main_window.py` for the main GUI class
- **Class Design:** Use a simple `MainWindow` class that exposes form values and handles GUI lifecycle
- **Minimal Interface:** GUI module should have a clean, simple interface for the business logic to interact with
- **Framework Agnostic Preparation:** Structure the separation in a way that makes future GUI framework changes easier
- **SOLID/DRY Implementation:** 
  - **Single Responsibility:** GUI module only handles display, app.py handles logic
  - **DRY:** Extract repeated GUI patterns without creating unnecessary abstractions
  - **Keep It Simple:** No overengineering - just clean separation of existing code

## Technical Considerations

- **Import Management:** Ensure no circular imports between GUI module and app.py
- **State Management:** GUI module should expose form values but not manage validation or business state
- **Event Callbacks:** Business logic functions (like `process_order`) should be passed to GUI as callbacks
- **Dependency Direction:** GUI module depends on business logic, not vice versa
- **Testing Isolation:** The separation should make it easier to test business logic without GUI dependencies

## Success Metrics

1. **Line Count Reduction:** app.py reduced from 459 lines to ~150 lines
2. **Clean Separation:** GUI code completely separated from business logic
3. **Functional Preservation:** All existing GUI functionality works identically after extraction
4. **Import Clarity:** Clear, non-circular dependency structure between modules
5. **Future-Ready:** GUI extraction positioned to enable future framework migration

## Open Questions

1. Should the progress window be part of the main window class or a separate module?
2. How should GUI configuration (colors, fonts, sizing) be handled - in the GUI module or configurable?
3. Should we create any intermediate abstractions to further decouple from tkinter specifics?