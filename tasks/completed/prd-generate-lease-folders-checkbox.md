# Product Requirements Document: Generate Lease Folders Checkbox

## Introduction/Overview
This feature adds an optional checkbox to the Order Manager GUI that allows users to control whether lease directories are created during order processing. The feature addresses the need for users who sometimes want to generate only the Excel worksheet without creating the associated folder structure for each lease.

## Goals
1. Provide users with control over directory creation during order processing
2. Add a new "Options" section to the GUI for future extensibility
3. Maintain all existing functionality when directories are enabled
4. Reduce processing time for users who don't need directory structure
5. Keep the interface simple and intuitive

## User Stories
- **As a user**, I want a checkbox to control whether lease directories are created, so that I can choose to generate only the Excel worksheet when I don't need the folder structure
- **As a user**, I want the checkbox to default to unchecked (directories disabled), so that I'm not creating unnecessary folders unless I specifically need them
- **As a user**, I want an "Options" section in the GUI, so that future configuration options can be added in a logical place
- **As a user**, I want the option to work the same way for both State and Federal order processing, so that the interface is consistent

## Functional Requirements
1. **R1**: Add a new "Options" section to the GUI positioned between the file selection row and the Process Order button
2. **R2**: Add a checkbox labeled "Generate Lease Folders" within the Options section
3. **R3**: Set the checkbox to default to unchecked (disabled) on application startup
4. **R4**: Reset the checkbox to unchecked state when the reset_gui() function is called
5. **R5**: When checkbox is unchecked, execute only create_order_worksheet() and skip create_folders() method call
6. **R6**: When checkbox is checked, execute both create_order_worksheet() and create_folders() methods (current behavior)
7. **R7**: Apply the same checkbox behavior to both NMStateOrderProcessor and FederalOrderProcessor
8. **R8**: Maintain the existing success message without modification regardless of checkbox state

## Non-Goals (Out of Scope)
- Persistence of checkbox state between application sessions
- User feedback messages about skipped directory creation
- Modification of the create_folders() method implementation
- Changes to the Excel worksheet generation logic
- Additional options or checkboxes beyond the lease folders option

## Design Considerations
- Use tkinter Frame widget to create a visually distinct "Options" section
- Position the Options section with appropriate padding to maintain visual hierarchy
- Use standard tkinter Checkbutton widget for consistency with existing UI
- Adjust window height from current 350px to accommodate the new Options section (approximately 390-400px)
- Maintain the current window width (600px) and overall layout structure
- Ensure the Options section can accommodate future additional options

## Technical Considerations
- Modify the process_order() function to check checkbox state before calling create_folders()
- Update reset_gui() function to include checkbox reset functionality
- Adjust window_height variable in app.py from 350 to approximately 390-400 pixels
- No changes required to existing OrderProcessor classes (NMStateOrderProcessor, FederalOrderProcessor)
- No additional dependencies required - uses existing tkinter widgets
- Checkbox state should be accessible via tkinter BooleanVar for easy integration

## Success Metrics
- Checkbox correctly controls directory creation behavior
- All existing functionality works without regression when checkbox is checked
- Excel worksheet generation works correctly when checkbox is unchecked
- GUI layout maintains visual appeal and usability
- Reset functionality properly resets checkbox to default (unchecked) state

## Open Questions
None - all requirements have been clarified through user input. 