import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox

from tkcalendar import DateEntry

from src.core.processors import FederalOrderProcessor, NMSLOOrderProcessor
from src.integrations.dropbox.auth import DropboxAuthHandler
from src.integrations.dropbox.config import DropboxConfig
from src.integrations.dropbox.service import DropboxService


def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_file = ".env"
    if os.path.exists(env_file):
        try:
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()

            print("✅ .env file loaded successfully")
            print(f"   App Key: {'✅' if os.getenv('DROPBOX_APP_KEY') else '❌'}")
            print(f"   App Secret: {'✅' if os.getenv('DROPBOX_APP_SECRET') else '❌'}")
            print(
                f"   Access Token: {'✅' if os.getenv('DROPBOX_ACCESS_TOKEN') else '❌'}"
            )

        except Exception as e:
            print(f"⚠️ Warning: Could not load .env file: {e}")
    else:
        print("⚠️ Warning: .env file not found")


# Load environment variables from .env file at startup
load_env_file()


def reset_gui():
    """Reset all GUI selections to their default/blank state"""
    agency.set("Select Agency")
    order_type.set("Select Order Type")
    date_entry.set_date(datetime.now().date())  # Reset to today's date
    order_number_entry.delete(0, tk.END)  # Clear order number
    file_path_var.set("")  # Clear file selection
    generate_folders.set(False)  # Reset checkbox to unchecked (default)
    # Note: use_dropbox is intentionally not reset to preserve user's choice


def process_order():
    # Get GUI selections
    selected_agency = agency.get()
    selected_order_type = order_type.get()
    selected_order_date = date_entry.get_date()

    # Get Order Number
    selected_order_number = order_number_entry.get()

    # Validate Agency selection
    if selected_agency == "Select Agency":
        messagebox.showwarning(
            "No Agency Selected",
            "Please select an agency (State or Federal) before processing.",
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
        messagebox.showinfo("Not Implemented", "Abstract workflow is not implemented")
        return

    # Get the selected file from GUI
    order_form = file_path_var.get()

    # Check if file is selected
    if not order_form:
        messagebox.showwarning(
            "No File Selected", "Please select an Excel file before processing."
        )
        return

    # Validate selected file
    if not os.path.exists(order_form):
        messagebox.showerror(
            "File Not Found", f"The selected file does not exist:\n{order_form}"
        )
        return

    if not order_form.lower().endswith(".xlsx"):
        messagebox.showerror("Invalid File Type", "Please select an Excel file (.xlsx)")
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
        # Initialize Dropbox service if checkbox is checked
        dropbox_service = None
        if use_dropbox.get():
            try:
                # Show progress message
                root.update_idletasks()

                # Create simple token-based auth handler
                auth_handler = DropboxAuthHandler.create_simple_auth()

                if not auth_handler.is_authenticated():
                    messagebox.showwarning(
                        "Dropbox Authentication Failed",
                        "Could not authenticate with Dropbox.\nCheck your DROPBOX_ACCESS_TOKEN in .env file.\nContinuing without Dropbox links.",
                    )
                    dropbox_service = None
                else:
                    # Create config manager for directory paths
                    config_manager = DropboxConfig()

                    # Create Dropbox service with auth handler
                    dropbox_service = DropboxService(auth_handler, config_manager)

                    # Ensure service is authenticated (should already be ready)
                    dropbox_service.authenticate()

                    print(
                        "✅ Dropbox service initialized with token-based authentication"
                    )

            except Exception as e:
                messagebox.showwarning(
                    "Dropbox Error",
                    f"Dropbox initialization failed: {str(e)}\nContinuing without Dropbox links.",
                )
                dropbox_service = None

        if selected_agency == "State":
            order_processor = NMSLOOrderProcessor(
                order_form,
                selected_agency,
                selected_order_type,
                selected_order_date,
                selected_order_number,
                dropbox_service=dropbox_service,
            )
        elif selected_agency == "Federal":
            order_processor = FederalOrderProcessor(
                order_form,
                selected_agency,
                selected_order_type,
                selected_order_date,
                selected_order_number,
                dropbox_service=dropbox_service,
            )
        else:
            messagebox.showerror("Error", f"Unknown agency type: {selected_agency}")
            return
        order_processor.create_order_worksheet()

        # Only create folders if checkbox is checked
        if generate_folders.get():
            order_processor.create_folders()

        # Show success message and reset GUI
        messagebox.showinfo("Success", "Order processed successfully!")
        reset_gui()


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
agency_option = tk.OptionMenu(agency_frame, agency, "Select Agency", "State", "Federal")
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

generate_folders = tk.BooleanVar()
generate_folders.set(False)  # Default to unchecked (disabled)

generate_folders_checkbox = tk.Checkbutton(
    options_frame,
    text="Generate Lease Folders",
    variable=generate_folders,
    bg="lightgray",
    font=("Arial", 10),
)
generate_folders_checkbox.pack(side="left", padx=(10, 0))

# Dropbox Link Integration checkbox
use_dropbox = tk.BooleanVar()
use_dropbox.set(True)  # Default to checked (enabled)

use_dropbox_checkbox = tk.Checkbutton(
    options_frame,
    text="Add Dropbox Links",
    variable=use_dropbox,
    bg="lightgray",
    font=("Arial", 10),
)
use_dropbox_checkbox.pack(side="left", padx=(20, 0))

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
