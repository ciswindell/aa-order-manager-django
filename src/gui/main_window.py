"""Main window component for the Order Processor application."""

import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, scrolledtext, ttk
from typing import Optional

from tkcalendar import DateEntry


class ProcessingCancelledException(Exception):
    """Exception raised when user cancels processing."""


class ProgressManager:
    """Handles progress display and state management following SRP."""

    def __init__(self, progress_text, progress_bar, main_cancel_button):
        self.progress_text = progress_text
        self.progress_bar = progress_bar
        self.main_cancel_button = main_cancel_button
        self.cancel_requested = False

    def update_progress(self, message: str, percentage: Optional[int] = None) -> None:
        """Update progress display with color formatting."""
        if not self.progress_text:
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        message_type = self._determine_message_type(message)

        # Update text area with color formatting
        self.progress_text.config(state="normal")
        start_pos = self.progress_text.index(tk.END)
        self.progress_text.insert(tk.END, formatted_message + "\n")
        end_pos = self.progress_text.index(tk.END)
        self.progress_text.tag_add(
            message_type, f"{start_pos} linestart", f"{end_pos} lineend -1c"
        )
        self.progress_text.see(tk.END)
        self.progress_text.config(state="disabled")

        if percentage is not None:
            self.progress_bar["value"] = percentage

        # Check for cancellation
        if self.cancel_requested:
            raise ProcessingCancelledException("Processing cancelled by user")

    def _determine_message_type(self, message: str) -> str:
        """Determine message type for color formatting."""
        message_lower = message.lower()
        if any(
            keyword in message_lower
            for keyword in ["error", "failed", "exception", "crash"]
        ):
            return "error"
        if any(
            keyword in message_lower
            for keyword in ["warning", "warn", "caution", "skipping"]
        ):
            return "warning"
        if any(
            keyword in message_lower
            for keyword in ["complete", "success", "finished", "done"]
        ):
            return "success"
        return "info"

    def start_processing(self):
        """Start processing state."""
        self.cancel_requested = False
        self.main_cancel_button.config(state="normal", text="Cancel")
        self.progress_bar["value"] = 0
        self.clear_progress()

    def stop_processing(self):
        """Stop processing state."""
        self.main_cancel_button.config(state="disabled", text="Cancel")

    def cancel_processing(self):
        """Handle cancellation request."""
        self.cancel_requested = True
        self.main_cancel_button.config(state="disabled", text="Cancelling...")

    def clear_progress(self):
        """Clear progress display."""
        self.progress_text.config(state="normal")
        self.progress_text.delete(1.0, tk.END)
        self.progress_text.config(state="disabled")


class UIConstants:
    """UI styling constants to eliminate repetition."""

    BG_COLOR = "lightgray"
    FONT = ("Arial", 10)
    BUTTON_FONT = ("Arial", 12)
    LABEL_WIDTH = 12
    PADDING = 10
    BUTTON_COLOR = "lightblue"
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 550  # Increased to accommodate progress section
    OPTION_MENU_WIDTH = 15
    FILE_ENTRY_WIDTH = 35

    # Default form values
    DEFAULT_AGENCY = "Select Agency"
    DEFAULT_ORDER_TYPE = "Select Order Type"

    # Progress section styling
    PROGRESS_SECTION_HEIGHT = 150
    PROGRESS_TEXT_HEIGHT = 8
    PROGRESS_FONT = ("Courier New", 9)  # Monospace for terminal appearance


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

        # Progress section variables
        self.progress_frame = None
        self.progress_text = None
        self.progress_bar = None
        self.progress_manager = None

        # Form element references for state management
        self.form_elements = []
        self.process_button = None
        self.main_cancel_button = None

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

        # Progress section (initially hidden)
        self._create_progress_section(main_frame)

    def _create_form_row(self, parent, label_text, variable, default, *options):
        """Create a form row with label and option menu."""
        frame = self._create_row_frame(parent)
        self._create_label(frame, label_text)
        variable.set(default)
        option_menu = tk.OptionMenu(frame, variable, default, *options)
        option_menu.config(width=UIConstants.OPTION_MENU_WIDTH)
        option_menu.pack(side="left", padx=(UIConstants.PADDING, 0))

        # Store reference for state management
        self.form_elements.append(option_menu)

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

        # Store reference for state management
        self.form_elements.append(entry)
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

        browse_button = self._create_button(
            frame, text="Browse...", command=self._browse_file
        )

        # Store reference for state management
        self.form_elements.append(browse_button)

    def _create_button(
        self,
        parent,
        text,
        command,
        bg_color=None,
        fg_color=None,
        state="normal",
        side="left",
        padx=(0, 0),
    ):
        """Create a standardized button following DRY principles."""
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=UIConstants.BUTTON_FONT,
            bg=bg_color or UIConstants.BUTTON_COLOR,
            fg=fg_color or "black",
            relief="raised",
            padx=20,
            pady=5,
            state=state,
        )
        button.pack(side=side, padx=padx)
        return button

    def _create_process_button(self, parent):
        """Create the process order button with cancel button."""
        button_frame = tk.Frame(parent, bg=UIConstants.BG_COLOR)
        button_frame.pack(fill="x", pady=20)

        # Create inner frame to center the buttons
        inner_frame = tk.Frame(button_frame, bg=UIConstants.BG_COLOR)
        inner_frame.pack(expand=True)

        # Process Order button
        self.process_button = self._create_button(
            inner_frame,
            text="Process Order",
            command=self.process_order_callback,
            padx=(0, 10),
        )

        # Cancel button (always visible, but disabled when not processing)
        self.main_cancel_button = self._create_button(
            inner_frame,
            text="Cancel",
            command=self._cancel_processing,
            state="disabled",
        )

        # Store references for state management
        self.form_elements.append(self.process_button)

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

    def _create_progress_section(self, parent):
        """Create the embedded progress section (always visible)."""
        # Main progress frame
        self.progress_frame = tk.Frame(parent, bg=UIConstants.BG_COLOR)
        self.progress_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Progress label
        progress_label = tk.Label(
            self.progress_frame,
            text="Processing Status:",
            font=UIConstants.FONT,
            bg=UIConstants.BG_COLOR,
            anchor="w",
        )
        progress_label.pack(anchor="w", pady=(10, 5))

        # Text area for progress messages with scrollbar
        text_frame = tk.Frame(self.progress_frame, bg=UIConstants.BG_COLOR)
        text_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.progress_text = scrolledtext.ScrolledText(
            text_frame,
            height=UIConstants.PROGRESS_TEXT_HEIGHT,
            font=UIConstants.PROGRESS_FONT,
            bg="black",
            fg="lightgreen",
            insertbackground="lightgreen",
            state="disabled",  # Read-only
            wrap="word",
        )

        # Configure text tags for different message types
        self.progress_text.tag_configure("info", foreground="lightgreen")
        self.progress_text.tag_configure("warning", foreground="yellow")
        self.progress_text.tag_configure("error", foreground="red")
        self.progress_text.tag_configure("success", foreground="lightblue")

        self.progress_text.pack(fill="both", expand=True)

        # Progress bar frame (no cancel button here anymore)
        bottom_frame = tk.Frame(self.progress_frame, bg=UIConstants.BG_COLOR)
        bottom_frame.pack(fill="x", pady=(0, 10))

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            bottom_frame, mode="determinate", length=300
        )
        self.progress_bar.pack(fill="x")

        # Initialize progress manager following SRP
        self.progress_manager = ProgressManager(
            self.progress_text, self.progress_bar, self.main_cancel_button
        )

        # Add initial welcome message
        self.progress_text.config(state="normal")
        self.progress_text.insert(
            tk.END,
            "Ready to process orders. Select a file and click 'Process Order'.\n",
        )
        self.progress_text.config(state="disabled")

    def _cancel_processing(self):
        """Handle cancel button click - delegate to ProgressManager."""
        self.progress_manager.cancel_processing()

    def start_processing(self):
        """Start processing - delegate to ProgressManager and disable form elements."""
        self.progress_manager.start_processing()
        self.disable_form_elements()

    def stop_processing(self):
        """Stop processing - delegate to ProgressManager and re-enable form elements."""
        self.progress_manager.stop_processing()
        self.enable_form_elements()

    def disable_form_elements(self):
        """Disable all form elements during processing."""
        for element in self.form_elements:
            try:
                element.config(state="disabled")
            except tk.TclError:
                # Some widgets might not support state changes
                pass

    def enable_form_elements(self):
        """Re-enable all form elements after processing."""
        for element in self.form_elements:
            try:
                element.config(state="normal")
            except tk.TclError:
                # Some widgets might not support state changes
                pass

    def update_progress(self, message: str, percentage: Optional[int] = None) -> None:
        """Update progress (implements ProgressCallback protocol) - delegate to ProgressManager."""
        if self.progress_manager:
            self.progress_manager.update_progress(message, percentage)
            # Force UI update
            self.root.update()

    def run(self):
        """Start the main event loop."""
        self.root.mainloop()
