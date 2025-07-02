# Product Requirements Document: GUI Enhancement for Order Manager

## Introduction/Overview
This feature enhances the existing Order Manager GUI to prepare for future expansion while maintaining current functionality. The enhancement includes updating the agency selection terminology, adding order type selection, and implementing order date selection with automatic column prefilling capabilities.

## Goals
1. Modernize the GUI interface with more intuitive terminology
2. Add order type selection to support future workflow expansion
3. Implement order date selection for better order tracking
4. Automatically prefill output columns based on GUI selections
5. Maintain backward compatibility with existing workflow functionality

## User Stories
- **As a user**, I want to select "State" or "Federal" as agency types instead of the full names, so that the interface is more concise and user-friendly
- **As a user**, I want to select between "Runsheet" and "Abstract" order types, so that I can prepare for different types of order processing in the future
- **As a user**, I want to select an order date using a calendar picker, so that I can properly track when orders were created
- **As a user**, I want the Agency and Order Type columns in my output files to be automatically filled based on my GUI selections, so that I don't have to manually enter this information later
- **As a user**, I want to be notified when I select "Abstract" order type, so that I know this workflow is not yet implemented

## Functional Requirements
1. **R1**: Replace the current dropdown options "New Mexico State Orders" and "Federal Orders" with "State" and "Federal" respectively, with the label changed to "Agency"
2. **R2**: Add a new dropdown for "Order Type" with options "Runsheet" and "Abstract"
3. **R3**: Add a calendar date picker for "Order Date" selection
4. **R4**: When "Runsheet" is selected, execute the existing workflow without changes
5. **R5**: When "Abstract" is selected, display a popup message stating "Abstract workflow is not implemented"
6. **R6**: Prefill the "Agency" column in output files with "State" or "Federal" based on the Agency selection
7. **R7**: Prefill the "Order Type" column in output files with "Runsheet" or "Abstract" based on the Order Type selection
8. **R8**: Maintain all existing functionality when "Runsheet" is selected

## Non-Goals (Out of Scope)
- Implementation of the Abstract workflow functionality
- Changes to the existing Runsheet workflow logic
- Modification of folder creation logic
- Changes to Excel file output format beyond column prefilling

## Design Considerations
- Use tkinter's existing widget library for consistency
- Maintain the current window size and layout structure
- Use a calendar widget (tkcalendar) for date selection
- Ensure proper error handling for date selection

## Technical Considerations
- Must maintain compatibility with existing OrderProcessor classes
- Requires passing additional parameters (agency, order_type, order_date) to processors
- May need to install tkcalendar dependency for calendar widget
- Should update both NMStateOrderProcessor and FederalOrderProcessor to accept and use the new parameters

## Success Metrics
- All existing functionality works without regression
- New GUI elements are properly integrated and functional
- Output files contain correctly prefilled Agency and Order Type columns
- Calendar date picker works correctly across different operating systems

## Open Questions
- Should the Order Date be prefilled in a specific format in the output file?
- Should there be validation for the selected date (e.g., not in the future)?
- Should the Order Number field also be made interactive in the GUI for future use? 