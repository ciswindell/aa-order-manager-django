"""GUI application for processing order forms with cloud integration."""

import traceback
from tkinter import messagebox

from src.core.services.order_processor import OrderProcessorService
from src.gui.main_window import MainWindow, ProcessingCancelledException


def process_order(main_window):
    """Process the order using GUI selections."""
    # Get GUI form data
    form_data = main_window.get_form_data()

    if not form_data["file_path"]:
        return

    # Start processing - enable cancel and disable form
    main_window.start_processing()

    try:
        # Create order processor with MainWindow as progress callback
        order_processor = OrderProcessorService(progress_callback=main_window)

        # Process order from GUI data
        success, message, technical_details = order_processor.process_order_from_gui(
            form_data
        )

        # Stop processing - disable cancel and re-enable form
        main_window.stop_processing()

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

    except ProcessingCancelledException:
        # User cancelled processing
        main_window.stop_processing()
        messagebox.showinfo("Cancelled", "Order processing was cancelled by user.")

    except Exception as e:
        # Unexpected error during processing
        main_window.stop_processing()
        print(f"\n❌ UNEXPECTED ERROR in process_order(): {str(e)}")
        traceback.print_exc()
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")


def main():
    """Main entry point for the Order Processor application."""
    # Create the main window with process_order as callback
    main_window = MainWindow(lambda: process_order(main_window))

    # Start the application
    main_window.run()


if __name__ == "__main__":
    main()
