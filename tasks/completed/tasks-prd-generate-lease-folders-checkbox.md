# Task List: Generate Lease Folders Checkbox

## Relevant Files

- `app.py` - Main GUI application file that needs checkbox widget, options section, window sizing, and process logic modifications
- `processors.py` - Contains OrderProcessor classes but no changes needed per PRD

## Tasks

- [x] 1.0 Add Options GUI Section with Checkbox Widget
  - [x] 1.1 Create Options frame widget positioned between file selection and process button
  - [x] 1.2 Add "Options:" label to the frame with consistent styling (Arial 10pt, left-aligned)
  - [x] 1.3 Create BooleanVar variable for checkbox state management
  - [x] 1.4 Add Checkbutton widget labeled "Generate Lease Folders" with proper styling
  - [x] 1.5 Set checkbox default state to False (unchecked)
  - [x] 1.6 Apply consistent padding and layout (pady=10) to match existing GUI sections
  - [x] 1.7 Add visual border around options section for better separation

- [x] 2.0 Adjust Window Size and Layout  
  - [x] 2.1 Modify window_height variable from 350 to 390 pixels in app.py
  - [x] 2.2 Test window centering calculations work correctly with new height
  - [x] 2.3 Verify all GUI elements fit properly within the adjusted window size

- [x] 3.0 Implement Conditional Folder Creation Logic
  - [x] 3.1 Modify process_order() function to check checkbox state before calling create_folders()
  - [x] 3.2 Add conditional logic: if checkbox is checked, call create_folders(), if unchecked, skip it
  - [x] 3.3 Ensure create_order_worksheet() is always called regardless of checkbox state
  - [x] 3.4 Verify the logic works for both NMStateOrderProcessor and FederalOrderProcessor

- [x] 4.0 Update Reset Functionality
  - [x] 4.1 Modify reset_gui() function to include checkbox reset
  - [x] 4.2 Set checkbox BooleanVar to False when reset_gui() is called
  - [x] 4.3 Ensure reset happens after successful order processing

- [x] 5.0 Test Complete Implementation
  - [x] 5.1 Test State order processing with checkbox unchecked (worksheet only)
  - [x] 5.2 Test State order processing with checkbox checked (worksheet + folders)
  - [x] 5.3 Test Federal order processing with checkbox unchecked (worksheet only)  
  - [x] 5.4 Test Federal order processing with checkbox checked (worksheet + folders)
  - [x] 5.5 Test reset functionality properly resets checkbox to unchecked state
  - [x] 5.6 Verify success message displays correctly regardless of checkbox state 