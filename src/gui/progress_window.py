"""Progress window component for the Order Processor application."""

import tkinter as tk


class ProgressWindow:
    """Simple progress feedback window implementing ProgressCallback protocol."""

    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.progress_label = None

    def show(self):
        """Show the progress window."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Processing Order...")
        self.window.geometry("400x100")
        self.window.resizable(False, False)

        # Center on parent
        self.window.transient(self.parent)
        self.window.grab_set()

        # Progress label
        self.progress_label = tk.Label(
            self.window,
            text="Starting order processing...",
            font=("Arial", 10),
            wraplength=350,
            justify="center",
        )
        self.progress_label.pack(expand=True)

        # Update display
        self.window.update()

    def update_progress(self, message: str, _percentage: int = None):
        """Update progress message (implements ProgressCallback protocol)."""
        if self.progress_label:
            self.progress_label.config(text=message)
            self.window.update()

    def close(self):
        """Close the progress window."""
        if self.window:
            self.window.destroy()
            self.window = None
