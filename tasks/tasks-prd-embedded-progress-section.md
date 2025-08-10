# Task List: Embedded Progress Section Implementation

Based on PRD: `prd-embedded-progress-section.md`

## Relevant Files

- `src/gui/main_window.py` - Main window class that needs to implement ProgressCallback protocol and add progress section
- `src/gui/progress_window.py` - Existing progress window implementation to reference for ProgressCallback implementation
- `src/core/services/order_processor.py` - Contains ProgressCallback protocol definition and progress update calls
- `app.py` - Main application entry point that needs to be updated to use MainWindow instead of ProgressWindow
- `tests/gui/test_main_window.py` - Unit tests for MainWindow progress functionality (to be created)
- `tests/gui/test_progress_integration.py` - Integration tests for progress callback functionality (to be created)

### Notes

- Examine existing ProgressWindow implementation to understand current progress callback pattern
- Follow SOLID/DRY principles by reusing existing ProgressCallback protocol
- Keep implementation simple and avoid over-engineering
- Unit tests should verify progress section UI behavior and ProgressCallback protocol implementation

## Tasks

- [ ] 1.0 Analyze Existing Codebase and Plan Implementation
  - [ ] 1.1 Read and analyze ProgressWindow class to understand current ProgressCallback implementation pattern
  - [ ] 1.2 Read OrderProcessorService to identify all progress update calls and their context
  - [ ] 1.3 Review app.py integration between ProgressWindow and OrderProcessorService
  - [ ] 1.4 Search codebase for any other progress-related components or similar UI patterns
  - [ ] 1.5 Document findings and identify components that can be reused (DRY principle)
  - [ ] 1.6 Verify threading considerations and UI update patterns used in existing code

- [ ] 2.0 Update MainWindow Class to Support Progress Display
  - [ ] 2.1 Add progress section UI elements to _create_widgets method (frame, text area, progress bar, cancel button)
  - [ ] 2.2 Update UIConstants to include new window height (from 390 to ~550px) and progress section styling
  - [ ] 2.3 Implement ProgressCallback protocol by adding update_progress method to MainWindow
  - [ ] 2.4 Create _create_progress_section method following existing UI pattern conventions
  - [ ] 2.5 Add progress section visibility controls (show_progress_section, hide_progress_section methods)
  - [ ] 2.6 Add UI state management methods (disable_form_elements, enable_form_elements)
  - [ ] 2.7 Initialize progress section as hidden by default

- [ ] 3.0 Implement Progress Functionality
  - [ ] 3.1 Create scrollable Text widget with terminal-style appearance (monospace font, dark background)
  - [ ] 3.2 Implement automatic scrolling to bottom when new messages are added
  - [ ] 3.3 Add tkinter.ttk.Progressbar with determinate mode and percentage display
  - [ ] 3.4 Create cancel button with proper styling and event handling
  - [ ] 3.5 Implement message formatting with different colors for info/warning/error messages
  - [ ] 3.6 Add timestamp prefixes to progress messages for better tracking
  - [ ] 3.7 Implement progress text history management to prevent memory issues

- [ ] 4.0 Update Application Integration
  - [ ] 4.1 Modify process_order function in app.py to use MainWindow instead of ProgressWindow
  - [ ] 4.2 Remove ProgressWindow instantiation and show/close calls from app.py
  - [ ] 4.3 Add cancellation flag handling to OrderProcessorService (or use existing pattern)
  - [ ] 4.4 Update progress callback calls to handle cancellation state checking
  - [ ] 4.5 Ensure popup dialogs still appear for error-stopped processes (preserve existing messagebox calls)
  - [ ] 4.6 Add proper state cleanup when processing completes or is cancelled
  - [ ] 4.7 Test form reset functionality works correctly with new progress section

- [ ] 5.0 Testing and Validation
  - [ ] 5.1 Create test file tests/gui/test_main_window.py with basic MainWindow test setup
  - [ ] 5.2 Write unit tests for progress section UI creation and visibility controls
  - [ ] 5.3 Write unit tests for ProgressCallback protocol implementation (update_progress method)
  - [ ] 5.4 Write unit tests for UI state management (enable/disable form elements)
  - [ ] 5.5 Create integration test file tests/gui/test_progress_integration.py
  - [ ] 5.6 Write integration tests for end-to-end progress workflow with mock OrderProcessorService
  - [ ] 5.7 Test cancellation functionality with simulated long-running process
  - [ ] 5.8 Validate UI remains responsive during progress updates
  - [ ] 5.9 Manual testing: verify terminal-style output appearance and scrolling behavior
  - [ ] 5.10 Code review: verify no duplication exists and SOLID principles are followed