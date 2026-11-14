import cv2
import mediapipe as mp
import math

# Initialize mediapipe face mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Landmark indices for measuring face shape
LANDMARKS = {
    "chin": 152,
    "forehead": 10,
    "left_cheek": 234,
    "right_cheek": 454,
}

# Distance formula
def distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

# Face shape classifier
def classify_face_shape(width, height):
    ratio = height / width
    if ratio > 1.5:
        return "Oval", "Round or aviator frames suit you best."
    elif abs(height - width) < 0.05:
        return "Round", "Rectangle or square frames will balance your features."
    elif width > height:
        return "Square", "Round or oval glasses add softness."
    else:
        return "Heart", "Bottom-heavy frames balance your look."

# Start webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ ERROR: Could not open webcam.")
    exit()

print("✅ Webcam is active. Press 'q' to quit.")

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("❌ Frame capture failed.")
        continue

    # Convert to RGB
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_image)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Draw mesh
            mp_drawing.draw_landmarks(
                image=image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
            )

            # Calculate dimensions
            landmarks = face_landmarks.landmark
            face_width = distance(landmarks[LANDMARKS["left_cheek"]], landmarks[LANDMARKS["right_cheek"]])
            face_height = distance(landmarks[LANDMARKS["forehead"]], landmarks[LANDMARKS["chin"]])

            shape, suggestion = classify_face_shape(face_width, face_height)

            # Annotate results
            cv2.putText(image, f"Shape: {shape}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(image, suggestion, (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("Face Shape Detector", image)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
