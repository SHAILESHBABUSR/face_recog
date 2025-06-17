import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from datetime import datetime
import csv
import json

class FaceRecognitionApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Face Recognition Attendance System")
        self.window.geometry("1000x700")
        
        # Initialize variables
        self.cap = None
        self.is_running = False
        self.known_faces = []
        self.known_names = []
        self.known_ids = []
        self.name_id_map = {}
        self.next_id = 0
        self.recognition_threshold = 70  # LBPH confidence threshold (lower is better match)
        
        # Attendance tracking variables
        self.attendance_data = {}
        self.today_date = datetime.now().strftime("%Y-%m-%d")
        self.attendance_file = f"attendance_{self.today_date}.csv"
        self.load_attendance_data()
        
        # Initialize face detector and recognizer
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.window)
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Create left and right frames
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Create video frame
        self.video_frame = ttk.Label(self.left_frame)
        self.video_frame.pack(padx=10, pady=10)
        
        # Create control buttons frame
        self.control_frame = ttk.Frame(self.left_frame)
        self.control_frame.pack(padx=10, pady=5)
        
        # Create buttons
        self.start_button = ttk.Button(self.control_frame, text="Start Camera", command=self.start_camera)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(self.control_frame, text="Stop Camera", command=self.stop_camera, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.export_button = ttk.Button(self.control_frame, text="Export Attendance", command=self.export_attendance)
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        # Create status label
        self.status_label = ttk.Label(self.left_frame, text="Camera Status: Not Running")
        self.status_label.pack(pady=5)
        
        # Create attendance display
        self.create_attendance_display()
        
        # Load known faces
        self.load_known_faces()
        
        # Train the recognizer after loading faces
        if self.known_faces:
            self.face_recognizer.train(self.known_faces, np.array(self.known_ids))
            print("Face recognizer trained.")
        else:
            print("No known faces loaded for training.")
    
    def create_attendance_display(self):
        # Attendance title
        attendance_title = ttk.Label(self.right_frame, text="Today's Attendance", font=("Arial", 14, "bold"))
        attendance_title.pack(pady=10)
        
        # Create Treeview for attendance
        columns = ("Name", "Time", "Status")
        self.attendance_tree = ttk.Treeview(self.right_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        self.attendance_tree.heading("Name", text="Name")
        self.attendance_tree.heading("Time", text="Time")
        self.attendance_tree.heading("Status", text="Status")
        
        # Define column widths
        self.attendance_tree.column("Name", width=100)
        self.attendance_tree.column("Time", width=100)
        self.attendance_tree.column("Status", width=80)
        
        self.attendance_tree.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.attendance_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.attendance_tree.configure(yscrollcommand=scrollbar.set)
        
        # Summary frame
        summary_frame = ttk.Frame(self.right_frame)
        summary_frame.pack(pady=10, fill=tk.X)
        
        self.total_label = ttk.Label(summary_frame, text="Total Present: 0")
        self.total_label.pack(side=tk.LEFT, padx=10)
        
        self.known_count_label = ttk.Label(summary_frame, text=f"Known People: {len(self.name_id_map)}")
        self.known_count_label.pack(side=tk.RIGHT, padx=10)
    
    def load_attendance_data(self):
        """Load existing attendance data for today"""
        if os.path.exists(self.attendance_file):
            try:
                with open(self.attendance_file, 'r', newline='') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        name = row['Name']
                        time = row['Time']
                        status = row['Status']
                        if name not in self.attendance_data:
                            self.attendance_data[name] = {'time': time, 'status': status}
            except Exception as e:
                print(f"Error loading attendance data: {e}")
    
    def record_attendance(self, name):
        """Record attendance for a person"""
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # Only record if not already recorded today or if it's a new entry
        if name not in self.attendance_data:
            self.attendance_data[name] = {
                'time': current_time,
                'status': 'Present'
            }
            
            # Add to treeview
            self.attendance_tree.insert('', 'end', values=(name, current_time, 'Present'))
            
            # Update summary
            self.update_summary()
            
            # Save to file
            self.save_attendance_data()
            
            # Show notification
            messagebox.showinfo("Attendance Recorded", f"{name} marked present at {current_time}")
    
    def save_attendance_data(self):
        """Save attendance data to CSV file"""
        try:
            with open(self.attendance_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Name', 'Time', 'Status', 'Date'])
                for name, data in self.attendance_data.items():
                    writer.writerow([name, data['time'], data['status'], self.today_date])
        except Exception as e:
            print(f"Error saving attendance data: {e}")
    
    def update_summary(self):
        """Update the attendance summary"""
        total_present = len(self.attendance_data)
        self.total_label.config(text=f"Total Present: {total_present}")
        self.known_count_label.config(text=f"Known People: {len(self.name_id_map)}")
    
    def export_attendance(self):
        """Export attendance data to a more detailed format"""
        try:
            export_file = f"attendance_report_{self.today_date}.txt"
            with open(export_file, 'w') as file:
                file.write(f"ATTENDANCE REPORT - {self.today_date}\n")
                file.write("=" * 50 + "\n\n")
                file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                file.write("ATTENDANCE LIST:\n")
                file.write("-" * 30 + "\n")
                for name, data in self.attendance_data.items():
                    file.write(f"{name}: {data['time']} - {data['status']}\n")
                
                file.write(f"\nSUMMARY:\n")
                file.write("-" * 30 + "\n")
                file.write(f"Total Present: {len(self.attendance_data)}\n")
                file.write(f"Total Known People: {len(self.name_id_map)}\n")
                file.write(f"Attendance Rate: {(len(self.attendance_data)/len(self.name_id_map)*100):.1f}%\n")
            
            messagebox.showinfo("Export Successful", f"Attendance report exported to {export_file}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting attendance: {e}")
        
    def load_known_faces(self):
        # Dictionary mapping image filenames to names
        image_names = {
            "sharan.jpg": "Sharan",
            "shailesh.jpg": "Shailesh",
            "WIN_20250614_11_02_35_Pro.jpg": "sharan",
            "WIN_20250614_11_02_17_Pro.jpg": "shailesh",
            "WIN_20250614_11_41_46_Pro.jpg": "shailesh",
            "WIN_20250614_11_41_45_Pro.jpg": "shailesh",
            "WIN_20250614_11_41_44_Pro.jpg": "shailesh",
            "WIN_20250614_11_41_39_Pro.jpg": "shailesh",
            "WIN_20250614_11_41_41_Pro.jpg": "shailesh",
            "WIN_20250614_11_41_37_Pro.jpg": "shailesh",
            "WIN_20250614_11_49_50_Pro.jpg": "sharan",
            "WIN_20250614_11_49_48_Pro.jpg": "sharan",
            "WIN_20250614_11_49_44_Pro.jpg": "sharan",
            "WIN_20250614_11_49_41_Pro.jpg": "sharan",
            "WIN_20250614_11_49_33_Pro.jpg": "sharan",
            "WIN_20250614_11_49_31_Pro.jpg": "sharan",
            "WIN_20250614_11_48_29_Pro.jpg": "sharan",
            "WIN_20250614_11_48_27_Pro.jpg": "sharan",
            "WIN_20250614_11_48_24_Pro.jpg": "sharan",
            "WIN_20250614_11_48_21_Pro.jpg": "sharan",
            "WIN_20250617_23_15_01_Pro.jpg": "shailesh",
            "WIN_20250617_23_15_02_Pro.jpg": "shailesh",
            "WIN_20250617_23_15_03_Pro.jpg": "shailesh",
            "WIN_20250617_23_15_04_Pro.jpg": "shailesh",
            "WIN_20250617_23_15_05_Pro.jpg": "shailesh",
            "WIN_20250617_23_15_06_Pro.jpg": "shailesh",
            "WIN_20250617_23_14_55_Pro.jpg": "shailesh",
            "WIN_20250617_23_14_56_Pro.jpg": "shailesh",
            "WIN_20250617_23_14_57_Pro.jpg": "shailesh",
            "WIN_20250617_23_14_58_Pro.jpg": "shailesh",
            "WIN_20250617_23_14_59_Pro.jpg": "shailesh"
        }
        
        images_dir = "images"
        for filename in os.listdir(images_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(images_dir, filename)
                name = image_names.get(filename, f"Person {len(self.name_id_map) + 1}")
                
                # Assign a unique ID to each new name
                if name not in self.name_id_map:
                    self.name_id_map[name] = self.next_id
                    self.next_id += 1
                
                current_id = self.name_id_map[name]
                
                img = cv2.imread(image_path)
                if img is None:
                    print(f"Error: Could not load image {image_path}")
                    continue
                
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                
                if len(faces) > 0:
                    x, y, w, h = faces[0]
                    face_img = gray[y:y+h, x:x+w]
                    face_img = cv2.resize(face_img, (100, 100))
                    self.known_faces.append(face_img)
                    self.known_ids.append(current_id)
                    self.known_names.append(name) # Keep track of the actual name for display
                    print(f"Loaded face for {name} (ID: {current_id})")
                else:
                    print(f"No face detected in {image_path}")
        
        # Load existing attendance data into treeview
        for name, data in self.attendance_data.items():
            self.attendance_tree.insert('', 'end', values=(name, data['time'], data['status']))
        
        self.update_summary()
        self.status_label.config(text=f"Camera Status: Not Running (Loaded {len(self.known_faces)} faces)")
    
    def start_camera(self):
        if not self.is_running:
            self.cap = cv2.VideoCapture(0)
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text=f"Camera Status: Running (Loaded {len(self.known_faces)} faces)")
            self.update_frame()
    
    def stop_camera(self):
        if self.is_running:
            self.is_running = False
            if self.cap is not None:
                self.cap.release()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_label.config(text=f"Camera Status: Stopped (Loaded {len(self.known_faces)} faces)")
            self.video_frame.config(image='')
    
    def update_frame(self):
        if self.is_running:
            ret, frame = self.cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    face_roi = gray[y:y+h, x:x+w]
                    face_roi = cv2.resize(face_roi, (100, 100))
                    
                    predicted_id, confidence = self.face_recognizer.predict(face_roi)
                    
                    recognized_name = "Unknown"
                    color = (0, 0, 255) # Red for unknown
                    
                    # If confidence is below threshold, it's a good match
                    if confidence < self.recognition_threshold:
                        # Find the name corresponding to the predicted_id
                        for name, _id in self.name_id_map.items():
                            if _id == predicted_id:
                                recognized_name = name
                                color = (0, 255, 0) # Green for recognized
                                # Record attendance for recognized person
                                self.record_attendance(recognized_name)
                                break
                    
                    label = f"{recognized_name} ({confidence:.2f})"
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (640, 480))
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                
                self.video_frame.config(image=photo)
                self.video_frame.image = photo
            
            self.window.after(10, self.update_frame)
    
    def __del__(self):
        if self.cap is not None:
            self.cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop() 