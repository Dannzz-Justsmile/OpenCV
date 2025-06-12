# Fingerprint Identification Application

This project is a fingerprint identification application that allows users to create profiles, log in, and scan fingerprints for identification purposes. The application utilizes image processing techniques to enhance and analyze fingerprint images.

## Project Structure

```
Dannz App
├── embeddings                          # Face embeddings storage for login validation
├── finger_db                           # Database for fingerprint authentication
├── finger.exe                          # Handles fingerprint-based authentication
├── main.exe                            # Main face recognition logic
├── flap.exe                            # Game or additional functionality
├── finger.py                           # Python script for fingerprint authentication
├── face.py                             # Python script for face recognition
├── flap.py                             # Python script for game execution
├── assets                              # Image assets for application UI
│   ├── bird.png
│   ├── bird_down.png
│   ├── bird_up.png
│   ├── plane.png
│   ├── cloud.png
│   ├── boss.png
├── models                              # Machine learning models for facial recognition
│   ├── dlib_face_recognition_resnet_model_v1.dat
│   ├── mmod_human_face_detector.dat
│   ├── shape_predictor_5_face_landmarks.dat
│   ├── shape_predictor_68_face_landmarks.dat
├── requirements.txt                    # Python dependencies required for the project
├── README.md                           # Documentation for the project
├── LICENSE                             # MIT License file
```

## Recommended 

   ```
   save the app main folder at: "C:\Users\YourUsername\AppData\Local\"
   ```
   -> your draw_img_pass will location in C:\Users\YourUsername\AppData\Local\Dannz\finger_db\your_profile
## Setup Instructions

1. **Clone the repository**:
   ```
   git clone https://github.com/dannz510/Dannz
   cd Dannz
   ```

2. **Install dependencies**:
   Make sure you have Python installed, then run:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python src/Dannz.exe
   ```

2. Follow the on-screen instructions to create a profile or log in using your face recognition.

## Dependencies

This project requires the following Python packages:
- opencv-python   # Computer vision library for image processing
- dlib            # Machine learning and facial recognition toolkit
- numpy           # Numerical computing library for arrays and matrices
- PyQt5           # GUI toolkit for Python
- pickle          # Built-in module for serializing and deserializing objects
- subprocess      # Built-in module for executing system commands
- sys             # Built-in module for system-specific parameters and functions
- os              # Built-in module for interacting with the operating system

## Security & Authentication Process

1. Fingerprint Authentication (finger.exe)
- Users enroll fingerprints before login.
- Fingerprint data is stored in finger_db.
2. Face Recognition (main.exe)
- Detects faces and matches embeddings.
- Uses deep learning models for identification.
3. Access Control (flap.exe)
- Runs additional functionality after successful login.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

MIT License

Copyright (c) 2025 Dannz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.