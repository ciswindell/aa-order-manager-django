"""GUI application for processing order forms with cloud integration."""

import traceback
from tkinter import messagebox

from src.core.services.order_processor import OrderProcessorService
from src.gui.progress_window import ProgressWindow
from src.gui.main_window import MainWindow


def process_order(main_window):
    """Process the order using GUI selections."""
    # Get GUI form data
    form_data = main_window.get_form_data()

    if not form_data["file_path"]:
        return

    # Create progress window
    progress_window = ProgressWindow(main_window.root)
    progress_window.show()

    # Create order processor with progress callback
    order_processor = OrderProcessorService(progress_callback=progress_window)

    # Process order from GUI data
    success, message, technical_details = order_processor.process_order_from_gui(
        form_data
    )

    progress_window.close()

    if success:
        messagebox.showinfo(
            "Success", f"Order processed successfully!\nOutput: {message}"
        )
        main_window.reset_form()
    else:
        # Log technical details for debugging
        if technical_details:
            print(f"\n❌ ERROR in process_order(): {technical_details}")
            traceback.print_exc()

        messagebox.showerror("Error", message)


def main():
    """Main entry point for the Order Processor application."""
    # Create the main window with process_order as callback
    main_window = MainWindow(lambda: process_order(main_window))

    # Start the application
    main_window.run()


if __name__ == "__main__":
    main()
