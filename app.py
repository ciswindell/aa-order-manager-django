import os
import tkinter as tk
from tkinter import filedialog

from processors import FederalOrderProcessor, NMStateOrderProcessor


def process_order(order_group: str):
    # Get the downloads folder path based on the operating system
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")

    order_form = filedialog.askopenfilename(
        initialdir=downloads_path,
        title="Select Order Form",
        filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*")),
    )

    if order_form:
        if order_group == "New Mexico State Orders":
            order_processor = NMStateOrderProcessor(order_form)
        else:  # Federal Orders
            order_processor = FederalOrderProcessor(order_form)
        order_processor.create_order_worksheet()
        order_processor.create_folders()


root = tk.Tk()
root.geometry("250x250")
root.title("Order Processor")

order_type = tk.StringVar()
order_type.set("New Mexico State Orders")  # default value

order_type_option = tk.OptionMenu(
    root, order_type, "New Mexico State Orders", "Federal Orders"
)
order_type_option.pack()

process_button = tk.Button(
    root, text="Process Order", command=lambda: process_order(order_type.get())
)
process_button.pack()

root.mainloop()
