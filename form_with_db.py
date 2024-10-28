import tkinter as tk 
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import qrcode
from io import BytesIO
import json
import os
import sqlite3  # For database connection

# Database setup
def create_connection():
    conn = sqlite3.connect('vehicle_registration.db')
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        first_name TEXT,
                        last_name TEXT,
                        mobile_no TEXT,
                        address TEXT,
                        pincode TEXT,
                        vehicle_type TEXT,
                        vehicle_brand TEXT,
                        vehicle_number TEXT,
                        services TEXT,
                        total_price REAL,
                        qr_code BLOB
                    )''')
    conn.commit()
    conn.close()

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
    return img

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
    for service, price, var in services:
        if var.get() == 1:
            selected_services.append(f"{service} (₹{price})")
            total_price += price

    if not (first_name and last_name and mobile_no and vehicle_type and vehicle_brand and vehicle_number):
        messagebox.showerror("Error", "Please fill in all the required fields!")
        return

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
        "Total Price": total_price
    }
    qr_data = json.dumps(data)

    # Generate and save QR code
    img = generate_qr_code(qr_data)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_code_data = buffer.getvalue()

    # Save data to the database
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO users 
                      (first_name, last_name, mobile_no, address, pincode, vehicle_type, vehicle_brand, vehicle_number, services, total_price, qr_code)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (first_name, last_name, mobile_no, address, pincode, vehicle_type, vehicle_brand, vehicle_number, services_info, total_price, qr_code_data))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "User data and QR code saved successfully!")

    # Display QR code in the GUI
    buffer.seek(0)
    qr_img = Image.open(buffer)
    qr_img.thumbnail((200, 200))
    qr_photo = ImageTk.PhotoImage(qr_img)
    barcode_label.config(image=qr_photo)
    barcode_label.image = qr_photo

# GUI setup
root = tk.Tk()
root.title("Vehicle Registration Form")
root.configure(bg="#f0f0f5")

tk.Label(root, text="Vehicle Registration Form", font=("Arial", 18, "bold"), bg="#f0f0f5").grid(row=0, column=0, columnspan=2, pady=20)

# Form fields
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

# Services with prices
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

# Initialize the database table
create_table()

root.mainloop()
