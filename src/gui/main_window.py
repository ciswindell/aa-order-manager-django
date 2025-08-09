"""Main window component for the Order Processor application."""

import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog

from tkcalendar import DateEntry


class UIConstants:
    """UI styling constants to eliminate repetition."""

    BG_COLOR = "lightgray"
    FONT = ("Arial", 10)
    BUTTON_FONT = ("Arial", 12)
    LABEL_WIDTH = 12
    PADDING = 10
    BUTTON_COLOR = "lightblue"
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 390
    OPTION_MENU_WIDTH = 15
    FILE_ENTRY_WIDTH = 35

    # Default form values
    DEFAULT_AGENCY = "Select Agency"
    DEFAULT_ORDER_TYPE = "Select Order Type"


class MainWindow:
    """Main application window handling all GUI components."""

    def __init__(self, process_order_callback):
        """Initialize the main window with a callback for order processing."""
        self.process_order_callback = process_order_callback

        # Initialize the main window
        self.root = tk.Tk()
        self.root.title("Order Processor")
        self.root.configure(bg=UIConstants.BG_COLOR)

        # Center window on screen
        self._center_window()

        # Create form variables
        self.agency = tk.StringVar()
        self.order_type = tk.StringVar()
        self.file_path_var = tk.StringVar()

        # Build the GUI
        self._create_widgets()

    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main frame for better organization
        main_frame = tk.Frame(self.root, bg=UIConstants.BG_COLOR, padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        # Agency row
        self._create_form_row(
            main_frame,
            "Agency:",
            self.agency,
            UIConstants.DEFAULT_AGENCY,
            "NMSLO",
            "Federal",
        )

        # Order Type row
        self._create_form_row(
            main_frame,
            "Order Type:",
            self.order_type,
            UIConstants.DEFAULT_ORDER_TYPE,
            "Runsheet",
            "Abstract",
        )

        # Order Date row
        self.date_entry = self._create_date_row(main_frame)
        # Order Number row
        self.order_number_entry = self._create_entry_row(
            main_frame, "Order Number:", width=18
        )

        # File selection row
        self._create_file_selection_row(main_frame)

        # Process button
        self._create_process_button(main_frame)

    def _create_form_row(self, parent, label_text, variable, default, *options):
        """Create a form row with label and option menu."""
        frame = self._create_row_frame(parent)
        self._create_label(frame, label_text)
        variable.set(default)
        option_menu = tk.OptionMenu(frame, variable, default, *options)
        option_menu.config(width=UIConstants.OPTION_MENU_WIDTH)
        option_menu.pack(side="left", padx=(UIConstants.PADDING, 0))

    def _create_row_frame(self, parent):
        """Create a standard form row frame."""
        frame = tk.Frame(parent, bg=UIConstants.BG_COLOR)
        frame.pack(fill="x", pady=UIConstants.PADDING)
        return frame

    def _create_label(self, parent, text):
        """Create a standard form label."""
        label = tk.Label(
            parent,
            text=text,
            width=UIConstants.LABEL_WIDTH,
            anchor="w",
            bg=UIConstants.BG_COLOR,
            font=UIConstants.FONT,
        )
        label.pack(side="left")
        return label

    def _create_date_row(self, parent):
        """Create the order date input row."""
        frame = self._create_row_frame(parent)
        self._create_label(frame, "Order Date:")
        date_entry = DateEntry(
            frame,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="yyyy-mm-dd",
        )
        date_entry.set_date(datetime.now().date())
        date_entry.pack(side="left", padx=(UIConstants.PADDING, 0))
        return date_entry

    def _create_entry_row(self, parent, label_text, width=18):
        """Create a form row with label and text entry."""
        frame = self._create_row_frame(parent)
        self._create_label(frame, label_text)
        entry = tk.Entry(frame, width=width, font=UIConstants.FONT)
        entry.pack(side="left", padx=(UIConstants.PADDING, 0))
        return entry

    def _create_file_selection_row(self, parent):
        """Create the file selection row with entry and browse button."""
        frame = self._create_row_frame(parent)
        self._create_label(frame, "Select File:")

        file_entry = tk.Entry(
            frame,
            textvariable=self.file_path_var,
            width=UIConstants.FILE_ENTRY_WIDTH,
            font=UIConstants.FONT,
            state="readonly",
        )
        file_entry.pack(side="left", padx=(UIConstants.PADDING, 5))

        browse_button = tk.Button(
            frame,
            text="Browse...",
            command=self._browse_file,
            font=UIConstants.FONT,
            bg=UIConstants.BUTTON_COLOR,
            relief="raised",
            padx=UIConstants.PADDING,
        )
        browse_button.pack(side="left")

    def _create_process_button(self, parent):
        """Create the process order button."""
        button_frame = tk.Frame(parent, bg=UIConstants.BG_COLOR)
        button_frame.pack(fill="x", pady=20)
        process_button = tk.Button(
            button_frame,
            text="Process Order",
            command=self.process_order_callback,
            font=UIConstants.BUTTON_FONT,
            bg=UIConstants.BUTTON_COLOR,
            relief="raised",
            padx=20,
            pady=5,
        )
        process_button.pack()

    def _browse_file(self):
        """Open file dialog to select Excel order form."""
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        file_path = filedialog.askopenfilename(
            initialdir=downloads_path,
            title="Select Order Form",
            filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*")),
        )
        if file_path:
            self.file_path_var.set(file_path)

    def get_form_data(self):
        """Get all form data as a dictionary."""
        return {
            "agency": self.agency.get(),
            "order_type": self.order_type.get(),
            "order_date": self.date_entry.get_date(),
            "order_number": self.order_number_entry.get(),
            "file_path": self.file_path_var.get(),
        }

    def reset_form(self):
        """Reset all form fields to their default values."""
        self.agency.set(UIConstants.DEFAULT_AGENCY)
        self.order_type.set(UIConstants.DEFAULT_ORDER_TYPE)
        self.date_entry.set_date(datetime.now().date())
        self.order_number_entry.delete(0, tk.END)
        self.file_path_var.set("")

    def _center_window(self):
        """Center the window on screen."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width / 2 - UIConstants.WINDOW_WIDTH / 2)
        center_y = int(screen_height / 2 - UIConstants.WINDOW_HEIGHT / 2)
        self.root.geometry(
            f"{UIConstants.WINDOW_WIDTH}x{UIConstants.WINDOW_HEIGHT}+{center_x}+{center_y}"
        )

    def run(self):
        """Start the main event loop."""
        self.root.mainloop()
