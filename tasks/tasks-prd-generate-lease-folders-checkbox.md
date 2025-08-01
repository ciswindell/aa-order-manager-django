# Task List: Generate Lease Folders Checkbox

## Relevant Files

- `app.py` - Main GUI application file that needs checkbox widget, options section, and process logic modifications
- `processors.py` - Contains OrderProcessor classes but no changes needed per PRD

## Tasks

- [ ] 1.0 Add Options GUI Section with Checkbox Widget
  - [ ] 1.1 Create Options frame widget positioned between file selection and process button
  - [ ] 1.2 Add "Options:" label to the frame with consistent styling (Arial 10pt, left-aligned)
  - [ ] 1.3 Create BooleanVar variable for checkbox state management
  - [ ] 1.4 Add Checkbutton widget labeled "Generate Lease Folders" with proper styling
  - [ ] 1.5 Set checkbox default state to False (unchecked)
  - [ ] 1.6 Apply consistent padding and layout (pady=10) to match existing GUI sections

- [ ] 2.0 Adjust Window Size and Layout  
  - [ ] 2.1 Modify window_height variable from 350 to 390 pixels in app.py
  - [ ] 2.2 Test window centering calculations work correctly with new height
  - [ ] 2.3 Verify all GUI elements fit properly within the adjusted window size

- [ ] 3.0 Implement Conditional Folder Creation Logic
  - [ ] 3.1 Modify process_order() function to check checkbox state before calling create_folders()
  - [ ] 3.2 Add conditional logic: if checkbox is checked, call create_folders(), if unchecked, skip it
  - [ ] 3.3 Ensure create_order_worksheet() is always called regardless of checkbox state
  - [ ] 3.4 Verify the logic works for both NMStateOrderProcessor and FederalOrderProcessor

- [ ] 4.0 Update Reset Functionality
  - [ ] 4.1 Modify reset_gui() function to include checkbox reset
  - [ ] 4.2 Set checkbox BooleanVar to False when reset_gui() is called
  - [ ] 4.3 Ensure reset happens after successful order processing

- [ ] 5.0 Test Complete Implementation
  - [ ] 5.1 Test State order processing with checkbox unchecked (worksheet only)
  - [ ] 5.2 Test State order processing with checkbox checked (worksheet + folders)
  - [ ] 5.3 Test Federal order processing with checkbox unchecked (worksheet only)  
  - [ ] 5.4 Test Federal order processing with checkbox checked (worksheet + folders)
  - [ ] 5.5 Test reset functionality properly resets checkbox to unchecked state
  - [ ] 5.6 Verify success message displays correctly regardless of checkbox state 