# cnn_model_evaluator.py

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import to_categorical
import cv2

# --- Configuration ---
model_path = "models/cnn_face_shape_model.h5"
val_data_dir = "src/data/sorted_images"
image_size = (128, 128)
batch_size = 32

# --- Load model ---
model = load_model(model_path)

# --- Data generator (no shuffling for correct order) ---
def load_rgba_images_from_directory(directory, class_indices):
    data = []
    labels = []
    for class_name, class_idx in class_indices.items():
        class_dir = os.path.join(directory, class_name)
        if not os.path.isdir(class_dir):
            continue
        for fname in os.listdir(class_dir):
            if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(class_dir, fname)
                img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
                if img is None:
                    print(f"⚠️ Could not read image: {img_path}")
                    continue
                img = cv2.resize(img, image_size)
                if img.shape[-1] == 3:  # RGB only
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
                data.append(img)
                labels.append(class_idx)
    X = np.array(data, dtype=np.float32) / 255.0
    y = to_categorical(np.array(labels), num_classes=len(class_indices))
    return X, y

class_names = ['heart', 'oval', 'round', 'square']
class_indices = {name: i for i, name in enumerate(class_names)}
X_val, y_val = load_rgba_images_from_directory(val_data_dir, class_indices)


# --- Evaluate model ---
loss, accuracy = model.evaluate(X_val, y_val, verbose=1)
print(f"📊 Final Validation Accuracy: {accuracy:.2%}")
print(f"🧮 Final Validation Loss: {loss:.4f}")

# --- Predictions and true labels ---
y_pred_probs = model.predict(X_val)
y_pred = np.argmax(y_pred_probs, axis=1)
y_true = np.argmax(y_val, axis=1)
class_names = list(class_indices.keys())

# --- Classification Report ---
print("\n📋 Classification Report:")
print(classification_report(y_true, y_pred, target_names=class_names))

# --- Confusion Matrix ---
cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=class_names, yticklabels=class_names)
plt.title("🔍 Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
plt.show()
