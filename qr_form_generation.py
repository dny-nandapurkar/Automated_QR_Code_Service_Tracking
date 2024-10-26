import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import qrcode
from io import BytesIO
import json
import os  # For handling paths

# Function to generate QR code
def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    return img  # Return the generated QR image

# Function to handle form submission
def submit_form():
    first_name = first_name_entry.get()
    last_name = last_name_entry.get()
    mobile_no = mobile_no_entry.get()
    address = address_entry.get()
    pincode = pincode_entry.get()
    vehicle_type = vehicle_type_combo.get()
    vehicle_brand = vehicle_brand_entry.get()
    vehicle_number = vehicle_number_entry.get()

    # Collect selected services
    selected_services = []
    total_price = 0
    service_status = {}
    for service, price, var in services:
        if var.get() == 1:
            selected_services.append(f"{service} (₹{price})")
            total_price += price
            # Initialize service status as 'in process'
            service_status[service] = 'in process'

    if not (first_name and last_name and mobile_no and vehicle_type and vehicle_brand and vehicle_number):
        messagebox.showerror("Error", "Please fill in all the required fields!")
        return

    # Mobile number validation (10 digits)
    if len(mobile_no) != 10 or not mobile_no.isdigit():
        messagebox.showerror("Error", "Mobile number must be exactly 10 digits!")
        return

    # Combine all the data to store in the QR code
    services_info = ", ".join(selected_services)
    data = {
        "First Name": first_name, 
        "Last Name": last_name, 
        "Mobile No": mobile_no, 
        "Address": address, 
        "Pincode": pincode, 
        "Vehicle Type": vehicle_type, 
        "Vehicle Brand": vehicle_brand, 
        "Vehicle Number": vehicle_number, 
        "Services": selected_services, 
        "Total Price": total_price,
        "Service Status": service_status
    }

    qr_data = json.dumps(data)

    # Generate a QR code with the data
    img = generate_qr_code(qr_data)

    # Save the QR code as an image file
    folder_path = "D:/Major_Project/QR_Codes"  # Change this to your desired folder path

    # Check if the folder exists, if not, create it
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Define the filename using vehicle number or any other unique attribute
    filename = f"{vehicle_number}_qr_code.png"

    # Full path to save the QR code image
    file_path = os.path.join(folder_path, filename)

    # Save the QR code to the specified folder
    img.save(file_path)

    messagebox.showinfo("Success", f"QR Code saved to {file_path}")

    # Display QR code in the GUI
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    qr_img = Image.open(buffer)
    qr_img.thumbnail((200, 200))
    qr_photo = ImageTk.PhotoImage(qr_img)

    barcode_label.config(image=qr_photo)
    barcode_label.image = qr_photo  # Keep reference to prevent garbage collection

# GUI Setup
root = tk.Tk()
root.title("Vehicle Registration Form")
root.configure(bg="#f0f0f5")

# Title label
tk.Label(root, text="Vehicle Registration Form", font=("Arial", 18, "bold"), bg="#f0f0f5").grid(row=0, column=0, columnspan=2, pady=20)

# First Name
tk.Label(root, text="First Name", font=("Arial", 12), bg="#f0f0f5").grid(row=1, column=0, padx=10, pady=5, sticky='w')
first_name_entry = tk.Entry(root, font=("Arial", 12), width=25)
first_name_entry.grid(row=1, column=1, padx=10, pady=5)

# Last Name
tk.Label(root, text="Last Name", font=("Arial", 12), bg="#f0f0f5").grid(row=2, column=0, padx=10, pady=5, sticky='w')
last_name_entry = tk.Entry(root, font=("Arial", 12), width=25)
last_name_entry.grid(row=2, column=1, padx=10, pady=5)

# Mobile Number
tk.Label(root, text="Mobile No.", font=("Arial", 12), bg="#f0f0f5").grid(row=3, column=0, padx=10, pady=5, sticky='w')
mobile_no_entry = tk.Entry(root, font=("Arial", 12), width=25)
mobile_no_entry.grid(row=3, column=1, padx=10, pady=5)

# Address
tk.Label(root, text="Address", font=("Arial", 12), bg="#f0f0f5").grid(row=4, column=0, padx=10, pady=5, sticky='w')
address_entry = tk.Entry(root, font=("Arial", 12), width=25)
address_entry.grid(row=4, column=1, padx=10, pady=5)

# Pincode
tk.Label(root, text="Pincode", font=("Arial", 12), bg="#f0f0f5").grid(row=5, column=0, padx=10, pady=5, sticky='w')
pincode_entry = tk.Entry(root, font=("Arial", 12), width=25)
pincode_entry.grid(row=5, column=1, padx=10, pady=5)

# Vehicle Type
tk.Label(root, text="Vehicle Type", font=("Arial", 12), bg="#f0f0f5").grid(row=6, column=0, padx=10, pady=5, sticky='w')
vehicle_type_combo = ttk.Combobox(root, values=["Car", "Bike", "Truck"], font=("Arial", 12))
vehicle_type_combo.grid(row=6, column=1, padx=10, pady=5)

# Vehicle Brand
tk.Label(root, text="Vehicle Brand", font=("Arial", 12), bg="#f0f0f5").grid(row=7, column=0, padx=10, pady=5, sticky='w')
vehicle_brand_entry = tk.Entry(root, font=("Arial", 12), width=25)
vehicle_brand_entry.grid(row=7, column=1, padx=10, pady=5)

# Vehicle Number Plate
tk.Label(root, text="Vehicle Number Plate", font=("Arial", 12), bg="#f0f0f5").grid(row=8, column=0, padx=10, pady=5, sticky='w')
vehicle_number_entry = tk.Entry(root, font=("Arial", 12), width=25)
vehicle_number_entry.grid(row=8, column=1, padx=10, pady=5)

# Services with prices
tk.Label(root, text="Select Services", font=("Arial", 12), bg="#f0f0f5").grid(row=9, column=0, padx=10, pady=10, sticky='w')
services_frame = tk.Frame(root, bg="#f0f0f5")
services_frame.grid(row=9, column=1, padx=10, pady=5)

services = [
    ("Washing", 100, tk.IntVar()),
    ("Tyre Changing", 200, tk.IntVar()),
    ("Oil Change", 300, tk.IntVar()),
    ("Engine Checkup", 400, tk.IntVar()),
    ("Brake Adjustment", 150, tk.IntVar()),
    ("Battery Replacement", 500, tk.IntVar())
]

for i, (service, price, var) in enumerate(services):
    tk.Checkbutton(services_frame, text=f"{service} (₹{price})", variable=var, font=("Arial", 11), bg="#f0f0f5").grid(row=i, column=0, sticky='w')

# Submit Button
submit_button = tk.Button(root, text="Submit", command=submit_form, font=("Arial", 12), bg="#4CAF50", fg="white", width=15)
submit_button.grid(row=10, column=0, columnspan=2, pady=20)

# Barcode display (QR code)
barcode_label = tk.Label(root, bg="#f0f0f5")
barcode_label.grid(row=11, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()
