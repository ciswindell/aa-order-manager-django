"""GUI application for processing order forms with cloud integration."""

import os
import traceback
from pathlib import Path
from tkinter import messagebox

from src.core.services.order_processor import OrderProcessorService
from src.core.models import AgencyType
from src.integrations.cloud.factory import CloudServiceFactory
from src.gui.progress_window import ProgressWindow
from src.gui.main_window import MainWindow


def process_order(main_window):
    """Process the order using GUI selections and cloud integration."""
    # Get GUI form data
    form_data = main_window.get_form_data()

    # Create progress window
    progress_window = ProgressWindow(main_window.root)

    # Validate Agency selection
    if form_data["agency"] == "Select Agency":
        messagebox.showwarning(
            "No Agency Selected",
            "Please select an agency (NMSLO or Federal) before processing.",
        )
        return

    # Validate Order Type selection
    if form_data["order_type"] == "Select Order Type":
        messagebox.showwarning(
            "No Order Type Selected",
            "Please select an order type (Runsheet or Abstract) before processing.",
        )
        return

    # Check if Abstract is selected
    if form_data["order_type"] == "Abstract":
        messagebox.showinfo(
            "Not Implemented", "Abstract workflow is not yet implemented"
        )
        return

    # Validate Order Number format (optional but helpful)
    if (
        form_data["order_number"]
        and not form_data["order_number"].replace("-", "").replace("_", "").isalnum()
    ):
        messagebox.showwarning(
            "Invalid Order Number",
            "Order number should contain only letters, numbers, hyphens, and underscores.",
        )
        return

    # Get the selected file from GUI
    order_form = form_data["file_path"]

    # Check if file is selected
    if not order_form:
        messagebox.showwarning(
            "No File Selected",
            "Please select an Excel order form file before processing.\n\nClick 'Browse' to select your order form.",
        )
        return

    # Validate selected file
    if not os.path.exists(order_form):
        messagebox.showerror(
            "File Not Found",
            f"The selected file no longer exists:\n{order_form}\n\nPlease select a different file.",
        )
        return

    if not order_form.lower().endswith((".xlsx", ".xls")):
        messagebox.showerror(
            "Invalid File Type",
            f"Selected file is not an Excel file:\n{order_form}\n\nPlease select an Excel file (.xlsx or .xls)",
        )
        return

    try:
        # Test if file is accessible/readable
        with open(order_form, "rb"):
            pass
    except PermissionError:
        messagebox.showerror(
            "Access Denied", f"Cannot access the selected file:\n{order_form}"
        )
        return
    except (OSError, IOError) as e:
        messagebox.showerror("File Error", f"Error accessing file:\n{str(e)}")
        return

    if order_form:
        # Show progress window
        progress_window.show()

        try:
            # Create OrderData from GUI selections
            order_data = main_window.create_order_data()

            # Initialize cloud service
            progress_window.update_progress("Initializing cloud service...")
            cloud_service = CloudServiceFactory.create_service("dropbox")

            # Authenticate the cloud service
            try:
                cloud_service.authenticate()
            except (
                Exception
            ) as auth_error:  # noqa: E722 - Authentication can raise various error types
                progress_window.close()
                messagebox.showerror(
                    "Authentication Error",
                    f"Failed to authenticate with Dropbox: {auth_error}\n\n"
                    "Please check your DROPBOX_ACCESS_TOKEN in the .env file.",
                )
                return

            # Create order processor with progress callback
            order_processor = OrderProcessorService(cloud_service, progress_window)

            # Process order end-to-end
            # Convert GUI agency to enum
            agency_enum = (
                AgencyType.NMSLO if form_data["agency"] == "NMSLO" else AgencyType.BLM
            )

            # Save output to same directory as input file
            input_file_path = Path(order_form)
            output_directory = input_file_path.parent

            output_path = order_processor.process_order(
                order_data=order_data,
                order_form_path=input_file_path,
                output_directory=output_directory,
                agency=agency_enum,
            )

            progress_window.close()

            # Show success message and reset GUI
            messagebox.showinfo(
                "Success", f"Order processed successfully!\nOutput: {output_path}"
            )
            main_window.reset_form()

        except FileNotFoundError:
            progress_window.close()
            messagebox.showerror(
                "File Not Found",
                f"Could not find the order form file:\n{order_form}\n\nPlease check the file path and try again.",
            )
            return
        except PermissionError:
            progress_window.close()
            messagebox.showerror(
                "File Access Error",
                f"Permission denied accessing the file:\n{order_form}\n\nPlease check file permissions and try again.",
            )
            return
        except ValueError as e:
            progress_window.close()
            messagebox.showerror(
                "Invalid Data",
                f"Invalid data in the order form:\n{str(e)}\n\nPlease check the Excel file format and try again.",
            )
            return
        except ConnectionError:
            progress_window.close()
            messagebox.showerror(
                "Connection Error",
                "Unable to connect to Dropbox.\n\nPlease check your internet connection and Dropbox authentication.",
            )
            return
        except Exception as e:  # noqa: E722 - Catch-all for unexpected errors
            progress_window.close()
            error_msg = str(e)

            # ALWAYS log errors to console for debugging
            print(f"\n❌ ERROR in process_order(): {error_msg}")
            traceback.print_exc()

            if "authentication" in error_msg.lower():
                messagebox.showerror(
                    "Authentication Error",
                    "Dropbox authentication failed.\n\nPlease check your DROPBOX_ACCESS_TOKEN in the .env file.",
                )
            elif "column" in error_msg.lower():
                messagebox.showerror(
                    "Excel Format Error",
                    f"Problem with Excel file format:\n{error_msg}\n\nPlease ensure your order form has the required columns (Lease, Legal Description).",
                )
            elif "workflow" in error_msg.lower():
                messagebox.showerror(
                    "Workflow Error",
                    f"Error during workflow execution:\n{error_msg}\n\nSome items may not have been processed completely.",
                )
            else:
                messagebox.showerror(
                    "Processing Error",
                    f"An unexpected error occurred:\n{error_msg}\n\nPlease contact support if the problem persists.",
                )
            return


def main():
    """Main entry point for the Order Processor application."""
    # Create the main window with process_order as callback
    main_window = MainWindow(lambda: process_order(main_window))

    # Start the application
    main_window.run()


if __name__ == "__main__":
    main()
