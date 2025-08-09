# Task List: GUI Logic Extraction from app.py

## Relevant Files

- `src/gui/__init__.py` - Package initialization for GUI module
- `src/gui/main_window.py` - Main window GUI class extracted from app.py
- `src/gui/progress_window.py` - Progress window class extracted from app.py  
- `app.py` - Refactored main application file with GUI code removed

### Notes

- Keep existing tkinter dependencies and behavior exactly as-is
- Focus on clean separation without overengineering
- Follow SOLID/DRY principles while maintaining simplicity

## Tasks

- [ ] 1.0 Create GUI Module Structure
  - [ ] 1.1 Create `src/gui/` directory
  - [ ] 1.2 Create `src/gui/__init__.py` package file
  - [ ] 1.3 Verify import structure works from app.py

- [ ] 2.0 Extract ProgressWindow Class
  - [ ] 2.1 Create `src/gui/progress_window.py` file
  - [ ] 2.2 Move ProgressWindow class from app.py (lines 17-60)
  - [ ] 2.3 Add necessary imports (tkinter) to progress_window.py
  - [ ] 2.4 Update app.py to import ProgressWindow from gui module

- [ ] 3.0 Extract Main Window GUI Components
  - [ ] 3.1 Create `src/gui/main_window.py` file
  - [ ] 3.2 Create MainWindow class with __init__ method
  - [ ] 3.3 Move window setup code (lines 294-306) to MainWindow.__init__
  - [ ] 3.4 Move all form creation code (lines 307-441) to MainWindow class
  - [ ] 3.5 Create method to expose form values as dictionary
  - [ ] 3.6 Create method to reset form to default values
  - [ ] 3.7 Create method to run main event loop

- [ ] 4.0 Extract GUI Helper Functions
  - [ ] 4.1 Move browse_file function (lines 406-416) to main_window.py
  - [ ] 4.2 Move create_order_data_from_gui function (lines 62-78) to main_window.py
  - [ ] 4.3 Update function references to work within MainWindow class
  - [ ] 4.4 Eliminate duplicated label/frame creation patterns using simple helper method

- [ ] 5.0 Refactor app.py to Use GUI Module
  - [ ] 5.1 Add imports for MainWindow and ProgressWindow from gui module
  - [ ] 5.2 Remove all GUI creation code (lines 294-458)
  - [ ] 5.3 Remove ProgressWindow class definition (lines 17-60)
  - [ ] 5.4 Update process_order function to work with MainWindow instance
  - [ ] 5.5 Create main() function that instantiates MainWindow and starts app
  - [ ] 5.6 Verify all functionality works exactly as before
  - [ ] 5.7 Confirm app.py reduced to approximately 150 lines