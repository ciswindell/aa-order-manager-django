"""Main window component for the Order Processor application."""

import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog

from tkcalendar import DateEntry

from src.core.models import OrderData, ReportType


class MainWindow:
    """Main application window handling all GUI components."""

    def __init__(self, process_order_callback):
        """Initialize the main window with a callback for order processing."""
        self.process_order_callback = process_order_callback

        # Initialize the main window
        self.root = tk.Tk()
        self.root.title("Order Processor")
        self.root.configure(bg="lightgray")

        # Center window on screen
        window_width = 600
        window_height = 390
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        # Create form variables
        self.agency = tk.StringVar()
        self.order_type = tk.StringVar()
        self.file_path_var = tk.StringVar()

        # Build the GUI
        self._create_widgets()

    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main frame for better organization
        main_frame = tk.Frame(self.root, bg="lightgray", padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        # Agency row
        self._create_form_row(
            main_frame, "Agency:", self.agency, "Select Agency", "NMSLO", "Federal"
        )

        # Order Type row
        self._create_form_row(
            main_frame,
            "Order Type:",
            self.order_type,
            "Select Order Type",
            "Runsheet",
            "Abstract",
        )

        # Order Date row
        date_frame = tk.Frame(main_frame, bg="lightgray")
        date_frame.pack(fill="x", pady=10)
        tk.Label(
            date_frame,
            text="Order Date:",
            width=12,
            anchor="w",
            bg="lightgray",
            font=("Arial", 10),
        ).pack(side="left")
        self.date_entry = DateEntry(
            date_frame,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="yyyy-mm-dd",
        )
        self.date_entry.set_date(datetime.now().date())
        self.date_entry.pack(side="left", padx=(10, 0))

        # Order Number row
        order_number_frame = tk.Frame(main_frame, bg="lightgray")
        order_number_frame.pack(fill="x", pady=10)
        tk.Label(
            order_number_frame,
            text="Order Number:",
            width=12,
            anchor="w",
            bg="lightgray",
            font=("Arial", 10),
        ).pack(side="left")
        self.order_number_entry = tk.Entry(
            order_number_frame, width=18, font=("Arial", 10)
        )
        self.order_number_entry.pack(side="left", padx=(10, 0))

        # File selection row
        file_frame = tk.Frame(main_frame, bg="lightgray")
        file_frame.pack(fill="x", pady=10)
        tk.Label(
            file_frame,
            text="Select File:",
            width=12,
            anchor="w",
            bg="lightgray",
            font=("Arial", 10),
        ).pack(side="left")

        file_entry = tk.Entry(
            file_frame,
            textvariable=self.file_path_var,
            width=35,
            font=("Arial", 10),
            state="readonly",
        )
        file_entry.pack(side="left", padx=(10, 5))

        browse_button = tk.Button(
            file_frame,
            text="Browse...",
            command=self._browse_file,
            font=("Arial", 10),
            bg="lightblue",
            relief="raised",
            padx=10,
        )
        browse_button.pack(side="left")

        # Button frame for centered button
        button_frame = tk.Frame(main_frame, bg="lightgray")
        button_frame.pack(fill="x", pady=20)
        process_button = tk.Button(
            button_frame,
            text="Process Order",
            command=self.process_order_callback,
            font=("Arial", 12),
            bg="lightblue",
            relief="raised",
            padx=20,
            pady=5,
        )
        process_button.pack()

    def _create_form_row(self, parent, label_text, variable, default, *options):
        """Create a form row with label and option menu (DRY helper method)."""
        frame = tk.Frame(parent, bg="lightgray")
        frame.pack(fill="x", pady=10)
        tk.Label(
            frame,
            text=label_text,
            width=12,
            anchor="w",
            bg="lightgray",
            font=("Arial", 10),
        ).pack(side="left")
        variable.set(default)
        option_menu = tk.OptionMenu(frame, variable, default, *options)
        option_menu.config(width=15)
        option_menu.pack(side="left", padx=(10, 0))

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
        self.agency.set("Select Agency")
        self.order_type.set("Select Order Type")
        self.date_entry.set_date(datetime.now().date())
        self.order_number_entry.delete(0, tk.END)
        self.file_path_var.set("")

    def create_order_data(self):
        """Create OrderData from current GUI selections."""
        form_data = self.get_form_data()

        # Convert GUI values to enums
        report_type = (
            ReportType.RUNSHEET
            if form_data["order_type"] == "Runsheet"
            else ReportType.BASE_ABSTRACT
        )

        return OrderData(
            order_number=form_data["order_number"] or "Unknown",
            order_date=form_data["order_date"],
            order_type=report_type,
        )

    def run(self):
        """Start the main event loop."""
        self.root.mainloop()
