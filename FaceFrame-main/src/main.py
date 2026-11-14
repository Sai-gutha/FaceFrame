"""
FaceFrame AR Glasses Try-On System
==================================

This file implements a real-time AR glasses try-on system using computer vision and machine learning.

SYSTEM OVERVIEW:
- Detects faces using MediaPipe FaceLandmarker (478 3D landmarks, Tasks API)
- Classifies face shape using a CNN model (oval, round, square, heart)
- Overlays appropriate glasses based on face shape
- Provides real-time performance with frame skipping optimization

MAIN COMPONENTS:
1. Face Detection & Landmark Extraction
2. Face Shape Classification (CNN Model)
3. AR Glasses Overlay with Alpha Blending
4. UI Elements & Performance Optimization

PERFORMANCE FEATURES:
- Frame skipping (CNN runs every 3 frames)
- Vectorized alpha blending (5-10x faster than loops)
- Cached predictions for smooth display
"""

import sys
import time

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import face_mesh
from ui_elements import draw_glasses_prompt, draw_quit_button, is_inside_button

# ============================================================================
# MODEL & DATA LOADING
# ============================================================================
# Load pre-trained CNN model for face shape classification
model = load_model('models/cnn_face_shape_model.h5')
class_labels = ['heart', 'oval', 'round', 'square']

# Initialize MediaPipe FaceLandmarker for 3D face landmark detection.
# Uses the Tasks API; the legacy mp.solutions.face_mesh API was removed in
# mediapipe 0.10.30+. Landmark indices are unchanged (478 points with irises,
# equivalent to the old refine_landmarks=True).
face_landmarker = vision.FaceLandmarker.create_from_options(
    vision.FaceLandmarkerOptions(
        base_options=mp_tasks.BaseOptions(model_asset_path='models/face_landmarker.task'),
        running_mode=vision.RunningMode.VIDEO,
        num_faces=1,
        min_face_detection_confidence=0.5,
    )
)

# Load glasses images with transparency (PNG with alpha channel)
glasses_dict = {
    "oval": cv2.imread(f"assets/glasses/oval_glasses.png", cv2.IMREAD_UNCHANGED),
    "round": cv2.imread(f"assets/glasses/round_glasses.png", cv2.IMREAD_UNCHANGED),
    "square": cv2.imread(f"assets/glasses/square_glasses.png", cv2.IMREAD_UNCHANGED),
    "heart": cv2.imread(f"assets/glasses/heart_glasses.png", cv2.IMREAD_UNCHANGED),
}

# Vertical offset adjustments for different glasses types
vertical_offsets = {
    "oval": 0,
    "round": 0,
    "square": 20,  # Square glasses need adjustment
    "heart": 0,
}

# ============================================================================
# CAMERA & UI SETUP
# ============================================================================
def open_camera(width=1280, height=720, max_index=5):
    """
    Open the first camera that actually delivers a frame at the requested size.

    Index 0 is not always the webcam: on machines with a Windows Hello / IR
    camera, slot 0 often exists but cannot be read, so probe until a real
    frame arrives instead of assuming index 0.

    The resolution is applied before the first read on purpose -- changing it
    mid-stream invalidates the capture's frame buffer on the Windows MSMF
    backend and makes the next read() raise.

    Returns:
        An opened VideoCapture, or None if no camera produced a frame.
    """
    for index in range(max_index):
        candidate = cv2.VideoCapture(index)
        if candidate.isOpened():
            candidate.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            candidate.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            try:
                ok, _ = candidate.read()
            except cv2.error:
                ok = False  # backend accepted the size but cannot stream it
            if ok:
                print(f"Using camera index {index}")
                return candidate
        candidate.release()
    return None

WINDOW_NAME = "Face Shape Classification"

cap = open_camera()

if cap is None:
    print("Error: Could not open camera.")
    # The landmarker was constructed before the camera, so it needs releasing
    # even on this path. exit() is the interactive-interpreter builtin; a script
    # that may be imported or frozen should use sys.exit with a failure code.
    face_landmarker.close()
    sys.exit(1)

button_clicked = False
button_coords = (20, 20, 120, 60)

# The "remove your glasses" card shows until the user dismisses it. Its bounds
# are recomputed every frame because they scale with the frame, so the mouse
# callback hit-tests against the box that was actually drawn.
glasses_prompt_visible = True
glasses_prompt_coords = (0, 0, 0, 0)

# A dismissal should not outlive the person who made it: on a kiosk the second
# customer would never be told to take their glasses off. This prototype has no
# session concept, so an empty frame is the proxy -- once nobody has been in
# view for this long, whoever appears next is treated as a new person and the
# card comes back. Three seconds is comfortably longer than a detection dropout
# from a turned head or a hand across the face, which last a frame or two.
NEW_SESSION_GAP_SECONDS = 3.0
last_face_seen = None  # monotonic timestamp of the last frame holding a face

# ============================================================================
# PERFORMANCE OPTIMIZATION VARIABLES
# ============================================================================
frame_count = 0
timestamp_ms = 0  # Monotonic clock fed to FaceLandmarker.detect_for_video
SKIP_FRAMES = 3  # Run CNN every 3 frames for better performance
cached_shape_label = None
cached_confidence = None
mesh_style = 0  # Index into face_mesh.STYLES; cycled with the 'm' key

# ============================================================================
# UI CALLBACKS
# ============================================================================
def mouse_callback(event, x, y, flags, param):
    """Handle mouse clicks for the QUIT button and the glasses prompt"""
    global button_clicked, glasses_prompt_visible
    if event == cv2.EVENT_LBUTTONDOWN:
        if is_inside_button(x, y, button_coords):
            button_clicked = True
        elif glasses_prompt_visible and is_inside_button(x, y, glasses_prompt_coords):
            glasses_prompt_visible = False

cv2.namedWindow(WINDOW_NAME)
cv2.setMouseCallback(WINDOW_NAME, mouse_callback)

# ============================================================================
# CORE FUNCTIONS
# ============================================================================
def vectorized_alpha_blend(frame, glasses_img, x_offset, y_offset):
    """
    Efficiently overlay glasses on frame using NumPy vectorized operations.
    
    This function replaces slow pixel-by-pixel loops with fast NumPy operations
    for 5-10x performance improvement in alpha blending.
    
    Args:
        frame: Camera frame (BGR format)
        glasses_img: Glasses image with alpha channel (BGRA format)
        x_offset, y_offset: Position to place glasses
    
    Returns:
        Frame with glasses overlaid
    """
    h, w = glasses_img.shape[:2]
    frame_h, frame_w = frame.shape[:2]
    
    # Calculate valid regions for blending
    frame_y1 = max(0, y_offset)
    frame_y2 = min(frame_h, y_offset + h)
    frame_x1 = max(0, x_offset)
    frame_x2 = min(frame_w, x_offset + w)
    
    glasses_y1 = max(0, -y_offset)
    glasses_y2 = glasses_y1 + (frame_y2 - frame_y1)
    glasses_x1 = max(0, -x_offset)
    glasses_x2 = glasses_x1 + (frame_x2 - frame_x1)
    
    # Extract regions for blending
    frame_region = frame[frame_y1:frame_y2, frame_x1:frame_x2]
    glasses_region = glasses_img[glasses_y1:glasses_y2, glasses_x1:glasses_x2]
    
    if frame_region.size == 0 or glasses_region.size == 0:
        return frame
    
    # Vectorized alpha blending (much faster than loops)
    alpha = glasses_region[:, :, 3:4] / 255.0
    frame_region[:, :, :3] = (1 - alpha) * frame_region[:, :, :3] + alpha * glasses_region[:, :, :3]
    
    return frame

# ============================================================================
# MAIN PROCESSING LOOP
# ============================================================================
# The loop runs inside try/finally so the camera and the landmarker are always
# released. Previously the cleanup sat after the loop at module level, which
# meant any exception -- including Ctrl+C -- skipped it and left the webcam
# held open until the process died.
try:
    while True:
        # Capture and preprocess frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        frame = cv2.flip(frame, 1)  # Mirror effect
    
        draw_quit_button(frame)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        # detect_for_video requires strictly increasing timestamps
        timestamp_ms = max(timestamp_ms + 1, int(time.monotonic() * 1000))
        results = face_landmarker.detect_for_video(mp_image, timestamp_ms)

        if results.face_landmarks:
            # Restore the glasses card if the frame was empty long enough to
            # count as a new person stepping up. Checked here, on arrival,
            # rather than on a timer, so it is never re-shown to an empty room.
            now = time.monotonic()
            if last_face_seen is not None and now - last_face_seen >= NEW_SESSION_GAP_SECONDS:
                glasses_prompt_visible = True
            last_face_seen = now

            for landmarks in results.face_landmarks:
                h, w, _ = frame.shape

                # ================================================================
                # FACE MESH OVERLAY
                # ================================================================
                # Drawn before the glasses so the frames sit on top of the mesh.
                # This replaces a hand-written 108-entry index list that only held
                # 38 unique points -- the face oval traced forward, backward, then
                # forward again -- and is now sourced from MediaPipe's own topology.
                mesh_points = face_mesh.to_pixels(landmarks, w, h)
                face_mesh.draw(frame, mesh_points, mesh_style)

                # Debug: Print 3D coordinates every 30 frames
                if frame_count % 30 == 0:
                    print("3D landmark sample (nose tip):", landmarks[1].x, landmarks[1].y, landmarks[1].z)

                # ================================================================
                # FACE SHAPE CLASSIFICATION
                # ================================================================
                # Extract eye positions for glasses positioning
                left_eye = landmarks[33]
                right_eye = landmarks[263]
                lx, ly = int(left_eye.x * w), int(left_eye.y * h)
                rx, ry = int(right_eye.x * w), int(right_eye.y * h)
            
                # Calculate face bounding box with margin
                x1 = int(min(l.x for l in landmarks) * w)
                x2 = int(max(l.x for l in landmarks) * w)
                y1 = int(min(l.y for l in landmarks) * h)
                y2 = int(max(l.y for l in landmarks) * h)
                margin_scale = 0.2 
                face_height = y2 - y1
                y1 = max(0, int(y1 - face_height * margin_scale))
            
                # PERFORMANCE OPTIMIZATION: Run CNN every 3 frames
                face_img = frame[y1:y2, x1:x2] if frame_count % SKIP_FRAMES == 0 else None

                # An empty crop happens when the face reaches the edge of the frame.
                # Skip only the CNN pass: `continue` here used to abandon the whole
                # iteration, dropping the mesh and glasses too, which showed up as
                # flicker whenever the user moved toward the edge.
                if face_img is not None and face_img.size > 0:
                    try:
                        # Image preprocessing pipeline for CNN
                        face_resized = cv2.resize(face_img, (128, 128))
                    
                        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
                        lab = cv2.cvtColor(face_resized, cv2.COLOR_BGR2LAB)
                        l, a, b = cv2.split(lab)
                        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                        cl = clahe.apply(l)
                        enhanced = cv2.merge((cl, a, b))
                        face_clahe = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
                    
                        # Prepare input for CNN model
                        face_array = img_to_array(face_clahe) / 255.0
                        face_array = np.expand_dims(face_array, axis=0)
                    
                        # Add edge detection features
                        gray = cv2.cvtColor(face_clahe, cv2.COLOR_BGR2GRAY)
                        edges = cv2.Canny(gray, 100, 200)
                        edges = edges[..., np.newaxis] / 255.0
                        rgb_array = img_to_array(face_clahe) / 255.0
                        face_array = np.concatenate([rgb_array, edges], axis=-1)
                        face_array = np.expand_dims(face_array, axis=0)
                    
                        # Get predictions from CNN model
                        prediction = model.predict(face_array)[0]
                        top2_indices = prediction.argsort()[-2:][::-1]
                    
                        # Cache results for display
                        label_index = top2_indices[0]
                        cached_shape_label = class_labels[label_index]
                        cached_confidence = prediction[label_index]
                        second_index = top2_indices[1]
                        second_label = class_labels[second_index]
                        second_conf = prediction[second_index]
                    
                    except Exception as e:
                        print(f"Prediction Error: {e}")
                        cached_shape_label = None
                        cached_confidence = None
                    
                # ================================================================
                # UI DISPLAY & GLASSES OVERLAY
                # ================================================================
                if cached_shape_label is not None:
                    # Display face shape classification results
                    label = f"{cached_shape_label} ({cached_confidence * 100:.1f}%)"
                    second_line = f"Next: {second_label} ({second_conf * 100:.1f}%)"
                
                    # Position text on right side with blue color (#5092D8)
                    text_x = w - 250
                    blue_color = (184, 146, 80)  # BGR format
                    cv2.putText(frame, label, (text_x, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, blue_color, 2)
                    cv2.putText(frame, second_line, (text_x, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, blue_color, 2)
                
                    # AR Glasses Overlay
                    selected_glasses = glasses_dict.get(cached_shape_label)
                    if selected_glasses is not None and selected_glasses.shape[2] == 4:
                        # Calculate glasses position based on eye centers
                        eye_center_x = (lx + rx) // 2
                        eye_center_y = (ly + ry) // 2
                        eye_width = int(np.linalg.norm([rx - lx, ry - ly]) * 1.5)
                    
                        # Scale glasses to fit face
                        scale = eye_width / selected_glasses.shape[1]
                        new_w = int(selected_glasses.shape[1] * scale)
                        new_h = int(selected_glasses.shape[0] * scale)
                        resized_glasses = cv2.resize(selected_glasses, (new_w, new_h), interpolation=cv2.INTER_AREA)
                    
                        # Rotate glasses to match eye angle
                        angle = -np.degrees(np.arctan2(ry - ly, rx - lx))
                        M = cv2.getRotationMatrix2D((new_w // 2, new_h // 2), angle, 1)
                        rotated_glasses = cv2.warpAffine(resized_glasses, M, (new_w, new_h), 
                                                       flags=cv2.INTER_LINEAR, 
                                                       borderMode=cv2.BORDER_CONSTANT, 
                                                       borderValue=(0,0,0,0))
                    
                        # Position glasses on face
                        x_offset = eye_center_x - new_w // 2
                        y_offset = eye_center_y - new_h // 2 + vertical_offsets.get(cached_shape_label, 0)
                    
                        # Apply glasses overlay using vectorized alpha blending
                        frame = vectorized_alpha_blend(frame, rotated_glasses, x_offset, y_offset)
                    
                        # Display glasses info
                        glasses_text = f"Showing: {cached_shape_label} glasses"
                        cv2.putText(frame, glasses_text, (w - 300, h - 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, blue_color, 2)
                
        # Drawn last so the card sits above the mesh and the glasses overlay.
        if glasses_prompt_visible:
            glasses_prompt_coords = draw_glasses_prompt(frame)

        # Update frame counter and display
        frame_count += 1
        cv2.imshow(WINDOW_NAME, frame)
    
        # Read the key once per frame -- calling waitKey twice would double the
        # per-frame delay and halve the effective framerate.
        key = cv2.waitKey(1) & 0xFF

        if key == ord('d') and glasses_prompt_visible:
            glasses_prompt_visible = False

        if key == ord('m'):
            mesh_style = face_mesh.next_style(mesh_style)
            print(f"Mesh style: {face_mesh.style_name(mesh_style)}")

        # Exit conditions
        if button_clicked or key == ord('q'):
            break

        # OpenCV's HighGUI never delivers a window-close event, so clicking the
        # title bar X cannot be handled in a callback -- it has to be polled.
        # WND_PROP_VISIBLE reads 0 once the window is hidden and -1 once it is
        # destroyed, so anything below 1 means it is gone. Without this the loop
        # kept running against a dead window until the process was killed.
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            break

except KeyboardInterrupt:
    # Ctrl+C surfaces from inside MediaPipe's threaded dispatcher, which would
    # otherwise print a traceback from deep in the library. Nothing has gone
    # wrong -- the user asked to quit -- so report it as an ordinary exit.
    print("\nInterrupted.")

finally:
    # FaceLandmarker holds native graph resources that garbage collection does
    # not free, so close it explicitly alongside the capture device.
    face_landmarker.close()
    cap.release()
    cv2.destroyAllWindows()
