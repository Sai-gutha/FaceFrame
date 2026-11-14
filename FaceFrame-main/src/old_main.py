import sys
import platform
import os
import joblib
import cv2
import time
import csv
import webbrowser
import json
from collections import deque

is_android = hasattr(sys, 'getandroidapilevel') or 'ANDROID_ARGUMENT' in os.environ
print(f"🔍 is_android = {is_android}")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"📂 BASE_DIR = {BASE_DIR}")

is_android = False
print("🛠️ Overriding is_android to False for local testing")

if not is_android:
    model_path = os.path.join(BASE_DIR, "models", "face_shape_model.pkl")
    print(f"🔎 Final model path: {model_path}")
    # Ensure the model path is not overwritten or misinterpreted
    print(f"📁 Loading model from: {model_path}")
    if not os.path.exists(model_path):
        print(f"🚫 ERROR: Model file not found at {model_path}")
        sys.exit(1)
    model = joblib.load(model_path)
    sample_faces = {}
    sample_folder = os.path.join(BASE_DIR, "training_samples")
    for shape in ["oval", "round", "square", "heart"]:
        sample_path = os.path.join(sample_folder, f"{shape}.png")
        if os.path.exists(sample_path):
            sample_faces[shape] = cv2.imread(sample_path)
            print(f"Loaded sample image for {shape} face from {sample_path}")
        else:
            print(f"Sample image for {shape} face not found at {sample_path}")
    glasses_dir = os.path.join(BASE_DIR, "glasses")
    glasses_dict = {
        "oval": cv2.imread(os.path.join(glasses_dir, "oval_glasses.png"), cv2.IMREAD_UNCHANGED),
        "round": cv2.imread(os.path.join(glasses_dir, "round_glasses.png"), cv2.IMREAD_UNCHANGED),
        "square": cv2.imread(os.path.join(glasses_dir, "square_glasses.png"), cv2.IMREAD_UNCHANGED),
        "heart": cv2.imread(os.path.join(glasses_dir, "heart_glasses.png"), cv2.IMREAD_UNCHANGED),
    }
    for k, v in glasses_dict.items():
        if v is None:
            print(f"Failed to load glasses/{k}_glasses.png. Make sure it's in the glasses directory.")
        else:
            print(f"Loaded {k}_glasses image with shape: {v.shape}")
def classify_face_shape_landmarks(landmarks):
    # Use normalized x,y for each landmark
    flattened = []
    for lm in landmarks:
        flattened.extend([lm.x, lm.y])
    return model.predict([flattened])[0]

import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# --- Bifocal need detection with rolling average ---
bifocal_ear_buffer = deque(maxlen=15)  # Adjustable window size

def detect_bifocal_need(landmarks):
    LEFT_EYE_IDX = list(range(33, 42))
    RIGHT_EYE_IDX = list(range(263, 272))

    def eye_aspect_ratio(eye_points):
        v1 = np.linalg.norm(np.array([eye_points[1].x, eye_points[1].y]) - np.array([eye_points[5].x, eye_points[5].y]))
        v2 = np.linalg.norm(np.array([eye_points[2].x, eye_points[2].y]) - np.array([eye_points[4].x, eye_points[4].y]))
        h = np.linalg.norm(np.array([eye_points[0].x, eye_points[0].y]) - np.array([eye_points[3].x, eye_points[3].y]))
        return (v1 + v2) / (2.0 * h) if h != 0 else 0

    left_eye = [landmarks[i] for i in LEFT_EYE_IDX]
    right_eye = [landmarks[i] for i in RIGHT_EYE_IDX]

    left_ear = eye_aspect_ratio(left_eye)
    right_ear = eye_aspect_ratio(right_eye)

    avg_ear = (left_ear + right_ear) / 2
    bifocal_ear_buffer.append(avg_ear)

    rolling_avg_ear = np.mean(bifocal_ear_buffer)

    with open("bifocal_log.csv", "a") as log_file:
        log_file.write(f"{time.time()},{avg_ear:.4f},{rolling_avg_ear:.4f},{int(rolling_avg_ear < 0.21)}\n")

    return rolling_avg_ear < 0.21

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)

def detect_physical_glasses(frame, landmarks, image_width, image_height):
    # Define bounding boxes around both eyes
    LEFT_EYE_IDX = list(range(33, 42))
    RIGHT_EYE_IDX = list(range(263, 272))

    def get_eye_box(eye_indices):
        xs = [int(landmarks[i].x * image_width) for i in eye_indices]
        ys = [int(landmarks[i].y * image_height) for i in eye_indices]
        x_min, x_max = max(min(xs) - 5, 0), min(max(xs) + 5, image_width)
        y_min, y_max = max(min(ys) - 5, 0), min(max(ys) + 5, image_height)
        return x_min, y_min, x_max, y_max

    # Get eye regions
    lx1, ly1, lx2, ly2 = get_eye_box(LEFT_EYE_IDX)
    rx1, ry1, rx2, ry2 = get_eye_box(RIGHT_EYE_IDX)

    left_eye_region = frame[ly1:ly2, lx1:lx2]
    right_eye_region = frame[ry1:ry2, rx1:rx2]

    def edge_density(region):
        if region.size == 0:
            return 0
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        return np.sum(edges > 0) / edges.size

    left_density = edge_density(left_eye_region)
    right_density = edge_density(right_eye_region)

    avg_density = (left_density + right_density) / 2

    # Debug: show cropped eye regions
    # cv2.imshow("Left Eye", left_eye_region)
    # cv2.imshow("Right Eye", right_eye_region)

    # Debug: print densities

    return avg_density > 0.018, avg_density  # Return both detection flag and value

def process_frame(frame, log_file_path=None, store_branding=""):
    detected_shape = None
    shape_link_url = None
    bifocal_text = ""
    if is_android:
        # On Android, frame is RGBA from Preview
        frame = np.array(frame)
        frame_rgb = frame[:, :, :3]
    else:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    if store_branding:
        cv2.putText(frame, f"🏪 {store_branding}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    results = face_mesh.process(frame_rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            h, w = frame.shape[:2]
            left_eye = face_landmarks.landmark[33]  # Approximate left eye
            right_eye = face_landmarks.landmark[263]  # Approximate right eye

            chin = face_landmarks.landmark[152]
            forehead = face_landmarks.landmark[10]
            shape = classify_face_shape_landmarks(face_landmarks.landmark)
            shape_link_text = f"See more {shape} styles →"
            shape_link_url = {
                "oval": "db_oval.json",
                "round": "db_round.json",
                "square": "db_square.json",
                "heart": "db_heart.json"
            }.get(shape, "db_generic.json")
            # --- Bifocal detection output ---
            # Removed print statements related to bifocal and face shape detection

            detected_shape = shape

            lx, ly = int(left_eye.x * w), int(left_eye.y * h)
            rx, ry = int(right_eye.x * w), int(right_eye.y * h)

            wearing_glasses, avg_density = detect_physical_glasses(frame, face_landmarks.landmark, w, h)
            print(f"[DEBUG] Physical glasses detected: {wearing_glasses} | Edge density: {avg_density:.4f}")
            if not is_android:
                nose = face_landmarks.landmark[168]
                left = face_landmarks.landmark[5]
                right = face_landmarks.landmark[426]
                nx, ny = int(nose.x * w), int(nose.y * h)
                lx2, ly2 = int(left.x * w), int(left.y * h)
                rx2, ry2 = int(right.x * w), int(right.y * h)

                cv2.line(frame, (nx, ny), (lx2, ly2), (255, 255, 0), 1)
                cv2.line(frame, (nx, ny), (rx2, ry2), (255, 255, 0), 1)

                dist1 = np.linalg.norm(np.array([nx, ny]) - np.array([lx2, ly2]))
                dist2 = np.linalg.norm(np.array([nx, ny]) - np.array([rx2, ry2]))
                face_width = np.linalg.norm(np.array([lx2, ly2]) - np.array([rx2, ry2]))
                avg_dist = (dist1 + dist2) / 2.0
                cv2.putText(frame, f"avg: {avg_dist:.1f} / w: {face_width:.1f}", (10, frame.shape[0] - 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

            # Draw landmarks only if physical glasses are NOT detected, not android, and landmarks are reliable
            if not wearing_glasses and not is_android and face_landmarks and len(face_landmarks.landmark) > 0:
                mp_drawing.draw_landmarks(
                    frame,
                    face_landmarks,
                    mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1, circle_radius=0),
                )

            # Optional: show warning if physical glasses detected
            if wearing_glasses:
                cv2.putText(frame, "👓 Physical glasses detected", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            if not is_android and not wearing_glasses:
                selected_glasses = glasses_dict.get(shape)
                if selected_glasses is None:
                    full_path = os.path.join("glasses", f"{shape}_glasses.png")
                    selected_glasses = cv2.imread(full_path, cv2.IMREAD_UNCHANGED)
                    if selected_glasses is None:
                        print(f"STILL could not load: {full_path}")
                    else:
                        print(f"Loaded fallback image for {shape} from {full_path}")
                if selected_glasses is None:
                    print(f"No glasses image found for face shape: {shape}")
                else:
                    if selected_glasses.shape[2] != 4:
                        print(f"Glasses image for {shape} does not have alpha channel")
                    eye_width = int(np.linalg.norm([rx - lx, ry - ly]) * 1.5)
                    angle = -np.degrees(np.arctan2(ry - ly, rx - lx))
                    center = ((lx + rx) // 2, (ly + ry) // 2)

                    scale = eye_width / selected_glasses.shape[1]
                    new_w = int(selected_glasses.shape[1] * scale)
                    new_h = int(selected_glasses.shape[0] * scale)
                    resized_glasses = cv2.resize(selected_glasses, (new_w, new_h), interpolation=cv2.INTER_AREA)

                    M = cv2.getRotationMatrix2D((new_w // 2, new_h // 2), angle, 1)
                    rotated_glasses = cv2.warpAffine(resized_glasses, M, (new_w, new_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))

                    y_offset = int(new_h * 0.0)
                    x1, y1 = center[0] - new_w // 2, center[1] - new_h // 2 + y_offset
                    if (0 <= x1 < frame.shape[1]) and (0 <= y1 < frame.shape[0]):
                        h_range = min(new_h, frame.shape[0] - y1)
                        w_range = min(new_w, frame.shape[1] - x1)

                        for i in range(h_range):
                            for j in range(w_range):
                                alpha = rotated_glasses[i, j, 3] / 255.0
                                if alpha > 0:
                                    for c in range(3):
                                        frame[y1 + i, x1 + j, c] = (1 - alpha) * frame[y1 + i, x1 + j, c] + alpha * rotated_glasses[i, j, c]

                cv2.line(frame, (lx, ly), (rx, ry), (255, 0, 0), 2)
                bifocal_text = "⚠️ Bifocal issue?" if detect_bifocal_need(face_landmarks.landmark) else "👁️ Vision appears normal"
                cv2.putText(
                    frame,
                    f"{shape.capitalize()} face - Showing {shape} glasses",
                    (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (139, 0, 0),  # Dark blue in BGR
                    2,
                    cv2.LINE_AA,
                )
                cv2.putText(
                    frame,
                    bifocal_text,
                    (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2,
                    cv2.LINE_AA,
                )
                cv2.putText(
                    frame,
                    shape_link_text,
                    (w - 320, h - 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )
                # Draw a rectangle to indicate the clickable area for the link
                cv2.rectangle(frame, (w - 322, h - 50), (w - 2, h - 27), (255, 255, 255), 1)
                # Future: Detect mouse click in region (8,82)-(320,105) and open shape_link_url
            # Overlay the edge density on screen near the bottom left of the webcam feed
            cv2.putText(frame, f"Edge density: {avg_density:.4f}", (10, h - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    else:
        if not is_android:
            cv2.putText(
                frame,
                f"No face detected - last shape: {detected_shape or 'unknown'}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )
    if detected_shape:
        with open(log_file_path, "a", newline="") as log_file:
            writer = csv.writer(log_file)
            writer.writerow([time.time(), detected_shape, bifocal_text, shape_link_url])

    # Display last 3 log entries on screen
    if log_file_path and os.path.exists(log_file_path):
        try:
            with open(log_file_path, "r") as log_file:
                lines = log_file.readlines()[-3:]
                base_y = 160
                for i, line in enumerate(lines):
                    parts = line.strip().split(",")
                    if len(parts) >= 4:
                        _, shape, bifocal, _ = parts
                        text = f"{shape.capitalize()} – {bifocal}"
                        cv2.putText(frame, text, (10, base_y + i * 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 255, 200), 2)
        except Exception as e:
            print(f"Error reading log file: {e}")

    return frame, shape_link_url, detected_shape

def run_faceframe_session(client_username):
    with open(os.path.join(BASE_DIR, "clients.json"), "r") as f:
        clients = json.load(f)
    client_info = next((c for c in clients if c["username"] == client_username), None)
    store_branding = f"{client_info['name']} — {client_info['location']}" if client_info else client_username
    logs_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_file_path = os.path.join(logs_dir, f"{client_username}_log.csv")

    cap = None
    for backend in [cv2.CAP_AVFOUNDATION, cv2.CAP_QT, cv2.CAP_V4L2, 0]:
        cap = cv2.VideoCapture(1, backend)
        if cap.isOpened():
            print(f"✅ Webcam opened using backend: {backend}")
            break
    if not cap or not cap.isOpened():
        print("🚫 Failed to open webcam with all attempted backends.")
        return
    print("🎥 Webcam stream starting...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        processed, shape_link_url, detected_shape = process_frame(frame, log_file_path, store_branding)
        cv2.imshow("FaceFrame AR", processed)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        if key == ord('s') and shape_link_url:
            local_db_path = os.path.join(os.getcwd(), shape_link_url)
            if os.path.exists(local_db_path):
                with open(local_db_path, "r") as f:
                    glasses_data = json.load(f)
                    print(f"\n=== {detected_shape.upper()} GLASSES ===")
                    for item in glasses_data:
                        name = item.get("name", "Unnamed")
                        price = item.get("price", "N/A")
                        stock = "✅" if item.get("in_stock", False) else "❌"
                        print(f"{name} — ${price} {stock}")
                    print("========================\n")
            else:
                print(f"No database file found for {local_db_path}")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__" and not is_android:
    client_username = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    run_faceframe_session(client_username)