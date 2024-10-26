import cv2
from pyzbar.pyzbar import decode
from PIL import Image
import json
import tkinter as tk
from tkinter import ttk
import threading

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
        # Access the webcam (usually device 0)
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Decode any QR codes found in the frame
            decoded_objects = decode(frame)

            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                
                # Display the QR data (assumed to be JSON)
                self.display_info(qr_data)
                
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

    def display_info(self, qr_data):
        try:
            # Parse the QR code data as JSON
            data = json.loads(qr_data)

            # Debugging: Print the parsed JSON data
            print("Parsed QR Data:", data)

            # Check if required keys are in the data, else use default value
            first_name = data.get('first_name', 'N/A')
            last_name = data.get('last_name', 'N/A')
            vehicle_type = data.get('vehicle_type', 'N/A')
            vehicle_brand = data.get('vehicle_brand', 'N/A')
            vehicle_number = data.get('vehicle_number', 'N/A')

            # Display the parsed user and vehicle information
            self.user_info_label.config(text=f"Name: {first_name} {last_name}\n"
                                             f"Vehicle: {vehicle_type} {vehicle_brand} ({vehicle_number})")

            # Clear any existing service information
            for widget in self.services_frame.winfo_children():
                widget.destroy()

            # Display the services and their statuses
            services = data.get('services', {})
            for service, status in services.items():
                service_label = tk.Label(self.services_frame, text=f"{service}: {status}", font=("Helvetica", 12))
                service_label.pack(anchor='w')

                # Dropdown to select new status for the service
                service_status = ttk.Combobox(self.services_frame, values=["Pending", "In Process", "Completed"])
                service_status.current(0)  # Default to "Pending"
                service_status.pack(anchor='w')

                # Button to update the service status
                update_button = tk.Button(self.services_frame, text="Update Status", 
                                          command=lambda s=service, cb=service_status: self.update_service_status(s, cb.get()))
                update_button.pack(anchor='w')

        except json.JSONDecodeError:
            print("Error: Unable to decode QR data as JSON")

    def update_service_status(self, service, new_status):
        # Logic to update the service status
        print(f"Updating {service} to {new_status}")
        # Here, you'd add code to save the updated status, possibly by sending a request to a backend or updating a database


if __name__ == "__main__":
    root = tk.Tk()
    app = QRTrackingApp(root)
    root.mainloop()
