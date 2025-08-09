import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox

from tkcalendar import DateEntry

from src.core.services.order_processor import OrderProcessorService
from src.core.models import OrderData, AgencyType, ReportType
from src.integrations.dropbox.auth import create_dropbox_auth
from src.integrations.dropbox.service_legacy import DropboxServiceLegacy
from src.integrations.cloud.factory import CloudServiceFactory
from src import config  # Automatically loads environment variables


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

    def update_progress(self, message: str, percentage: int = None):
        """Update progress message (implements ProgressCallback protocol)."""
        if self.progress_label:
            self.progress_label.config(text=message)
            self.window.update()

    def close(self):
        """Close the progress window."""
        if self.window:
            self.window.destroy()
            self.window = None


def create_order_data_from_gui(
    selected_agency, selected_order_type, selected_order_date, selected_order_number
):
    """Create OrderData from GUI selections."""
    # Convert GUI values to enums
    report_type = (
        ReportType.RUNSHEET
        if selected_order_type == "Runsheet"
        else ReportType.BASE_ABSTRACT
    )

    return OrderData(
        order_number=selected_order_number or "Unknown",
        order_date=selected_order_date,
        order_type=report_type,
    )


def reset_gui():
    """Reset all GUI selections to their default/blank state"""
    agency.set("Select Agency")
    order_type.set("Select Order Type")
    date_entry.set_date(datetime.now().date())  # Reset to today's date
    order_number_entry.delete(0, tk.END)  # Clear order number
    file_path_var.set("")  # Clear file selection
    # Note: Dropbox integration is now standard for all orders


def process_order():
    # Get GUI selections
    selected_agency = agency.get()
    selected_order_type = order_type.get()
    selected_order_date = date_entry.get_date()

    # Get Order Number
    selected_order_number = order_number_entry.get()

    # Create progress window
    progress_window = ProgressWindow(root)

    # Validate Agency selection
    if selected_agency == "Select Agency":
        messagebox.showwarning(
            "No Agency Selected",
            "Please select an agency (NMSLO or Federal) before processing.",
        )
        return

    # Validate Order Type selection
    if selected_order_type == "Select Order Type":
        messagebox.showwarning(
            "No Order Type Selected",
            "Please select an order type (Runsheet or Abstract) before processing.",
        )
        return

    # Check if Abstract is selected
    if selected_order_type == "Abstract":
        messagebox.showinfo(
            "Not Implemented", "Abstract workflow is not yet implemented"
        )
        return

    # Validate Order Number format (optional but helpful)
    if (
        selected_order_number
        and not selected_order_number.replace("-", "").replace("_", "").isalnum()
    ):
        messagebox.showwarning(
            "Invalid Order Number",
            "Order number should contain only letters, numbers, hyphens, and underscores.",
        )
        return

    # Get the selected file from GUI
    order_form = file_path_var.get()

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
        with open(order_form, "rb") as test_file:
            pass
    except PermissionError:
        messagebox.showerror(
            "Access Denied", f"Cannot access the selected file:\n{order_form}"
        )
        return
    except Exception as e:
        messagebox.showerror("File Error", f"Error accessing file:\n{str(e)}")
        return

    if order_form:
        # Show progress window
        progress_window.show()

        try:
            # Create OrderData from GUI selections
            order_data = create_order_data_from_gui(
                selected_agency,
                selected_order_type,
                selected_order_date,
                selected_order_number,
            )

            # Initialize cloud service
            progress_window.update_progress("Initializing cloud service...")
            cloud_service = CloudServiceFactory.create_service("dropbox")

            # Authenticate the cloud service
            try:
                cloud_service.authenticate()
            except Exception as auth_error:
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
            from pathlib import Path

            # Convert GUI agency to enum
            agency_enum = (
                AgencyType.NMSLO if selected_agency == "NMSLO" else AgencyType.BLM
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
            reset_gui()

        except FileNotFoundError as e:
            progress_window.close()
            messagebox.showerror(
                "File Not Found",
                f"Could not find the order form file:\n{order_form}\n\nPlease check the file path and try again.",
            )
            return
        except PermissionError as e:
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
        except ConnectionError as e:
            progress_window.close()
            messagebox.showerror(
                "Connection Error",
                "Unable to connect to Dropbox.\n\nPlease check your internet connection and Dropbox authentication.",
            )
            return
        except Exception as e:
            progress_window.close()
            error_msg = str(e)

            # ALWAYS log errors to console for debugging
            import traceback

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


root = tk.Tk()
root.title("Order Processor")
root.configure(bg="lightgray")

# Center window on screen
window_width = 600
window_height = 390
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)
root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

# Main frame for better organization
main_frame = tk.Frame(root, bg="lightgray", padx=20, pady=20)
main_frame.pack(expand=True, fill="both")

# Agency row
agency_frame = tk.Frame(main_frame, bg="lightgray")
agency_frame.pack(fill="x", pady=10)
tk.Label(
    agency_frame,
    text="Agency:",
    width=12,
    anchor="w",
    bg="lightgray",
    font=("Arial", 10),
).pack(side="left")
agency = tk.StringVar()
agency.set("Select Agency")  # default value
agency_option = tk.OptionMenu(agency_frame, agency, "Select Agency", "NMSLO", "Federal")
agency_option.config(width=15)
agency_option.pack(side="left", padx=(10, 0))

# Order Type row
order_type_frame = tk.Frame(main_frame, bg="lightgray")
order_type_frame.pack(fill="x", pady=10)
tk.Label(
    order_type_frame,
    text="Order Type:",
    width=12,
    anchor="w",
    bg="lightgray",
    font=("Arial", 10),
).pack(side="left")
order_type = tk.StringVar()
order_type.set("Select Order Type")  # default value
order_type_option = tk.OptionMenu(
    order_type_frame, order_type, "Select Order Type", "Runsheet", "Abstract"
)
order_type_option.config(width=15)
order_type_option.pack(side="left", padx=(10, 0))

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
date_entry = DateEntry(
    date_frame,
    width=12,
    background="darkblue",
    foreground="white",
    borderwidth=2,
    date_pattern="yyyy-mm-dd",
)
date_entry.set_date(datetime.now().date())
date_entry.pack(side="left", padx=(10, 0))

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
order_number_entry = tk.Entry(order_number_frame, width=18, font=("Arial", 10))
order_number_entry.pack(side="left", padx=(10, 0))

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

file_path_var = tk.StringVar()
file_entry = tk.Entry(
    file_frame,
    textvariable=file_path_var,
    width=35,
    font=("Arial", 10),
    state="readonly",
)
file_entry.pack(side="left", padx=(10, 5))


def browse_file():
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    file_path = filedialog.askopenfilename(
        initialdir=downloads_path,
        title="Select Order Form",
        filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*")),
    )
    if file_path:
        file_path_var.set(file_path)


browse_button = tk.Button(
    file_frame,
    text="Browse...",
    command=browse_file,
    font=("Arial", 10),
    bg="lightblue",
    relief="raised",
    padx=10,
)
browse_button.pack(side="left")

# Options frame for future configuration options
options_frame = tk.Frame(main_frame, bg="lightgray", relief="ridge", bd=1)
options_frame.pack(fill="x", pady=10)
tk.Label(
    options_frame,
    text="Options:",
    width=12,
    anchor="w",
    bg="lightgray",
    font=("Arial", 10),
).pack(side="left")

# Note: Legacy options removed - Dropbox links now standard, folder generation handled by workflows

# Button frame for centered button
button_frame = tk.Frame(main_frame, bg="lightgray")
button_frame.pack(fill="x", pady=20)
process_button = tk.Button(
    button_frame,
    text="Process Order",
    command=process_order,
    font=("Arial", 12),
    bg="lightblue",
    relief="raised",
    padx=20,
    pady=5,
)
process_button.pack()

root.mainloop()
