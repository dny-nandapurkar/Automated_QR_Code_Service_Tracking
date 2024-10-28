import cv2
from pyzbar.pyzbar import decode
from PIL import Image
import json
import tkinter as tk
from tkinter import ttk
import threading
import sqlite3  # For database connection

class QRTrackingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Garage Service Tracking")
        
        # User Information Display
        self.user_info_label = tk.Label(root, text="No Vehicle Scanned", font=("Helvetica", 14))
        self.user_info_label.pack(pady=10)

        # Frame to hold services and their statuses
        self.services_frame = tk.Frame(root)
        self.services_frame.pack(pady=10)

        # Start QR code scanning
        scan_button = tk.Button(root, text="Start Scanning", command=self.start_scan)
        scan_button.pack(pady=10)

    def start_scan(self):
        # Open a separate thread to avoid blocking the UI while scanning
        scan_thread = threading.Thread(target=self.scan_qr_code)
        scan_thread.start()

    def scan_qr_code(self):
        # Use DirectShow as the backend (Windows-specific) and set frame dimensions
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Check if the camera opened successfully
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break

            # Decode any QR codes found in the frame
            decoded_objects = decode(frame)

            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                
                # Parse vehicle number from the QR data
                data = json.loads(qr_data)
                vehicle_number = data.get("Vehicle Number", None)
                
                # Fetch and display information from the database
                if vehicle_number:
                    self.fetch_and_display_info(vehicle_number)
                
                # Stop the loop after detecting a QR code
                cap.release()
                cv2.destroyAllWindows()
                return

            # Display the webcam feed
            cv2.imshow('QR Code Scanner', frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def fetch_and_display_info(self, vehicle_number):
        try:
            # Connect to the database and fetch user data based on vehicle number
            conn = sqlite3.connect('vehicle_registration.db')
            cursor = conn.cursor()
            cursor.execute('''SELECT first_name, last_name, vehicle_type, vehicle_brand, services 
                              FROM users WHERE vehicle_number = ?''', (vehicle_number,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                first_name, last_name, vehicle_type, vehicle_brand, services_json = result
                
                # Display user and vehicle information
                self.user_info_label.config(text=f"Name: {first_name} {last_name}\n"
                                                 f"Vehicle: {vehicle_type} {vehicle_brand} ({vehicle_number})")

                # Clear existing service information
                for widget in self.services_frame.winfo_children():
                    widget.destroy()

                # Display services and statuses
                services = json.loads(services_json)
                for service, status in services.items():
                    service_label = tk.Label(self.services_frame, text=f"{service}: {status}", font=("Helvetica", 12))
                    service_label.pack(anchor='w')

                    # Dropdown to select new status for the service
                    service_status = ttk.Combobox(self.services_frame, values=["Pending", "In Process", "Completed"])
                    service_status.set(status)  # Set current status
                    service_status.pack(anchor='w')

                    # Button to update the service status
                    update_button = tk.Button(self.services_frame, text="Update Status", 
                                              command=lambda s=service, cb=service_status: self.update_service_status(s, cb.get(), vehicle_number))
                    update_button.pack(anchor='w')

            else:
                self.user_info_label.config(text="No data found for this vehicle.")

        except sqlite3.Error as e:
            print("Database error:", e)
        except json.JSONDecodeError:
            print("Error decoding services JSON.")

    def update_service_status(self, service, new_status, vehicle_number):
        # Update the service status in the database
        try:
            conn = sqlite3.connect('vehicle_registration.db')
            cursor = conn.cursor()

            # Fetch existing services, update the status for the specified service
            cursor.execute("SELECT services FROM users WHERE vehicle_number = ?", (vehicle_number,))
            services = json.loads(cursor.fetchone()[0])
            services[service] = new_status

            # Save the updated services back to the database
            cursor.execute("UPDATE users SET services = ? WHERE vehicle_number = ?", (json.dumps(services), vehicle_number))
            conn.commit()
            conn.close()

            # Update UI
            print(f"Updated {service} to {new_status} for vehicle {vehicle_number}")

        except sqlite3.Error as e:
            print("Error updating service status:", e)

# Run the Tkinter application
if __name__ == "__main__":
    root = tk.Tk()
    app = QRTrackingApp(root)
    root.mainloop()
