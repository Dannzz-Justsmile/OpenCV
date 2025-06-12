import cv2
import dlib
import numpy as np
import os
import sys
import pickle
import subprocess
from PyQt5 import QtWidgets, QtGui

# Directories for storing enrolled face embeddings
EMBEDDINGS_DIR = "embeddings"
if not os.path.exists(EMBEDDINGS_DIR):
    os.makedirs(EMBEDDINGS_DIR)

# Path for storing the embeddings mapping (username -> embedding)
EMBEDDINGS_PATH = os.path.join(EMBEDDINGS_DIR, "embeddings.pickle")

# Load or initialize the embeddings database as a dictionary.
# It maps a username to a 128-d numpy array (the averaged embedding).
if os.path.exists(EMBEDDINGS_PATH):
    with open(EMBEDDINGS_PATH, "rb") as f:
        embeddings_db = pickle.load(f)
else:
    embeddings_db = {}

# Required dlib model files (download these and place in your working directory)
SHAPE_PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"
FACE_RECOGNITION_MODEL_PATH = "dlib_face_recognition_resnet_model_v1.dat"

# Verify that the required model files exist
for model_path in [SHAPE_PREDICTOR_PATH, FACE_RECOGNITION_MODEL_PATH]:
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Required model file '{model_path}' not found!")

# Initialize dlib’s face detector, shape predictor, and face recognition model.
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(SHAPE_PREDICTOR_PATH)
face_rec_model = dlib.face_recognition_model_v1(FACE_RECOGNITION_MODEL_PATH)

def get_face_embedding(image):
    """
    Given a color image (BGR) that contains a face, detect the face,
    compute the facial landmarks, and then return the 128-D embedding.
    If no face is detected, return None.
    """
    # Convert to RGB since dlib models usually expect RGB
    rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    detections = detector(rgb_img, 1)
    if len(detections) == 0:
        return None
    # For simplicity, process only the first detected face.
    face_rect = detections[0]
    shape = sp(rgb_img, face_rect)
    face_descriptor = face_rec_model.compute_face_descriptor(rgb_img, shape)
    return np.array(face_descriptor)

def enroll_user(username, num_samples=5):
    """
    Enroll a new user by capturing num_samples images from the webcam,
    computing each face embedding, and saving the average embedding to disk.
    The captured embeddings are averaged to provide a more robust representation.
    
    The webcam frame is flipped horizontally (mirroring) so enrollment matches login.
    """
    cap = cv2.VideoCapture(0)
    embeddings = []
    captured = 0
    print(f"[Enroll] Starting enrollment for {username}. Look at the camera and press 'c' to capture.")

    while captured < num_samples:
        ret, frame = cap.read()
        if not ret:
            continue
        # Correct mirror effect
        frame = cv2.flip(frame, 1)
        # Copy for display and add instructions
        display = frame.copy()
        cv2.putText(display, f"Press 'c' to capture ({captured+1}/{num_samples})", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.imshow("Enroll - Press 'c' to capture", display)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            emb = get_face_embedding(frame)
            if emb is not None:
                embeddings.append(emb)
                captured += 1
                print(f"[Enroll] Captured sample {captured}")
            else:
                print("[Enroll] No face detected, please try again.")
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if len(embeddings) == 0:
        print("[Enroll] Enrollment failed: no face samples captured.")
        return None

    avg_embedding = np.mean(embeddings, axis=0)
    embeddings_db[username] = avg_embedding
    # Save updated embeddings database
    with open(EMBEDDINGS_PATH, "wb") as f:
        pickle.dump(embeddings_db, f)
    print(f"[Enroll] Enrollment complete for {username}.")
    return avg_embedding

def recognize_user(username, threshold=0.6):
    """
    Recognize the given user by comparing the embedding captured live against the stored
    embedding. If the Euclidean distance is below the threshold, the face is considered recognized.
    
    The live capture is processed continuously until a match is found or 'q' is pressed.
    """
    if username not in embeddings_db:
        print(f"[Recognize] No enrollment data for {username}.")
        return False

    enrolled_embedding = embeddings_db[username]
    cap = cv2.VideoCapture(0)
    recognized = False

    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        display = frame.copy()
        emb = get_face_embedding(frame)
        if emb is not None:
            # Compute Euclidean distance between enrolled and captured embedding
            dist = np.linalg.norm(enrolled_embedding - emb)
            cv2.putText(display, f"Distance: {dist:.3f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            if dist < threshold:
                recognized = True
                cv2.putText(display, "Access Granted", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.imshow("Recognition - Press 'q' to quit", display)
                cv2.waitKey(1500)
                break
            else:
                cv2.putText(display, "Access Denied", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.imshow("Recognition - Press 'q' to quit", display)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return recognized

def unlock_system():
    """Simulate unlocking the system and launch flap.exe."""
    print("[SYSTEM] System unlocked.")
    try:
        subprocess.Popen("flap.exe", shell=True)
        print("[SYSTEM] flap.exe launched successfully.")
    except Exception as e:
        print("[SYSTEM] Failed to launch flap.exe:", e)

def lock_system():
    """Simulate system lock."""
    print("[SYSTEM] System locked.")

# PyQt interface below

class FaceLockApp(QtWidgets.QWidget):
    def __init__(self):
        super(FaceLockApp, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Face Recognition Lock (dlib Embeddings)")
        self.setGeometry(300, 300, 400, 300)
        layout = QtWidgets.QVBoxLayout()

        self.lblTitle = QtWidgets.QLabel("🔐 Face Lock System")
        self.lblTitle.setFont(QtGui.QFont("Arial", 18))
        layout.addWidget(self.lblTitle)

        self.enrollBtn = QtWidgets.QPushButton("Enroll Account")
        self.enrollBtn.clicked.connect(self.enroll_account)
        layout.addWidget(self.enrollBtn)

        self.loginBtn = QtWidgets.QPushButton("Login")
        self.loginBtn.clicked.connect(self.login_account)
        layout.addWidget(self.loginBtn)

        self.exitBtn = QtWidgets.QPushButton("Exit")
        self.exitBtn.clicked.connect(self.close)
        layout.addWidget(self.exitBtn)

        self.setLayout(layout)

    def enroll_account(self):
        username, ok = QtWidgets.QInputDialog.getText(self, "Enroll Account", "Enter new username:")
        if ok and username:
            if username in embeddings_db:
                QtWidgets.QMessageBox.warning(self, "Error", "Username already exists!")
                return
            avg_emb = enroll_user(username)
            if avg_emb is not None:
                QtWidgets.QMessageBox.information(self, "Enrollment", f"User {username} enrolled successfully!")
            else:
                QtWidgets.QMessageBox.warning(self, "Enrollment", "Enrollment failed; no face data captured.")

    def login_account(self):
        accounts = list(embeddings_db.keys())
        if not accounts:
            QtWidgets.QMessageBox.warning(self, "Error", "No enrolled accounts found! Please enroll first.")
            return
        username, ok = QtWidgets.QInputDialog.getItem(self, "Login", "Select account:", accounts, 0, False)
        if ok and username:
            recognized = recognize_user(username)
            if recognized:
                unlock_system()  # Launch flap.exe after successful recognition
                QtWidgets.QMessageBox.information(self, "Access Granted", f"Welcome, {username}!")
            else:
                lock_system()
                QtWidgets.QMessageBox.warning(self, "Access Denied", f"Face not recognized for {username}.")

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = FaceLockApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()