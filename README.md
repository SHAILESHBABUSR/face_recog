# Face Recognition Attendance System

A real-time face recognition system that automatically tracks attendance with timestamps and stores attendance records.

## Features

- **Real-time Face Recognition**: Uses OpenCV and LBPH face recognizer for accurate face detection and recognition
- **Automatic Attendance Tracking**: Records attendance with timestamps when a known person is detected
- **Attendance Storage**: Saves attendance data to CSV files with date tracking
- **GUI Interface**: User-friendly Tkinter interface with live video feed and attendance display
- **Export Functionality**: Export attendance reports in text format
- **Daily Attendance Tracking**: Separate attendance files for each day

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have the `images` folder with face images for training the system.

## Usage

1. **Prepare Face Images**: 
   - Place face images in the `images` folder
   - The system automatically maps image filenames to person names
   - Supported formats: JPG, JPEG, PNG

2. **Run the Application**:
```bash
python face_recognition.py
```

3. **Using the Interface**:
   - Click "Start Camera" to begin face recognition
   - The system will automatically detect and recognize faces
   - When a known person is detected, attendance is automatically recorded
   - View attendance records in the right panel
   - Click "Export Attendance" to save a detailed report

## File Structure

```
realtime project/
├── face_recognition.py      # Main application
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── images/                 # Face images for training
│   ├── sharan.jpg
│   ├── shailesh.jpg
│   └── ... (other face images)
├── attendance_YYYY-MM-DD.csv  # Daily attendance files (auto-generated)
└── attendance_report_YYYY-MM-DD.txt  # Exported reports (auto-generated)
```

## Attendance Tracking

- **Automatic Recording**: Attendance is recorded when a known person is detected
- **Timestamp**: Each attendance entry includes the exact time of detection
- **Daily Files**: Separate CSV files are created for each day
- **No Duplicates**: Each person is recorded only once per day
- **Real-time Display**: Current attendance is shown in the GUI

## Output Files

### CSV Attendance File (`attendance_YYYY-MM-DD.csv`)
```
Name,Time,Status,Date
Sharan,09:15:30,Present,2024-01-15
Shailesh,09:20:45,Present,2024-01-15
```

### Text Report File (`attendance_report_YYYY-MM-DD.txt`)
```
ATTENDANCE REPORT - 2024-01-15
==================================================

Generated on: 2024-01-15 17:30:00

ATTENDANCE LIST:
------------------------------
Sharan: 09:15:30 - Present
Shailesh: 09:20:45 - Present

SUMMARY:
------------------------------
Total Present: 2
Total Known People: 2
Attendance Rate: 100.0%
```

## Configuration

- **Recognition Threshold**: Adjust `self.recognition_threshold` in the code (default: 70)
  - Lower values = stricter matching
  - Higher values = more lenient matching
- **Face Detection**: Uses Haar Cascade classifier for face detection
- **Face Recognition**: Uses LBPH (Local Binary Pattern Histogram) face recognizer

## Troubleshooting

1. **Camera not working**: Make sure your webcam is connected and not being used by another application
2. **Poor recognition**: 
   - Add more face images for each person
   - Ensure good lighting in the training images
   - Adjust the recognition threshold
3. **No faces detected**: Check that the `images` folder contains valid face images

## Dependencies

- `opencv-python`: Computer vision library for face detection and recognition
- `opencv-contrib-python`: Additional OpenCV modules including face recognition
- `numpy`: Numerical computing library
- `Pillow`: Python Imaging Library for image processing
- `tkinter`: GUI framework (included with Python)

## License

This project is open source and available under the MIT License.
