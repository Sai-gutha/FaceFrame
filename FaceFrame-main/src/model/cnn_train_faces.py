# cnn_train_faces.py

import os
import shutil
import json

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import cv2
import numpy as np

# Step 1: Sort images based on cluster_results.json
def sort_images():
    json_path = "src/data/cluster_results.json"
    source_folder = "src/data/raw_images"
    target_root = "src/data/sorted_images"

    cluster_label_map = {
        0: "round",
        1: "oval",
        2: "heart",
        3: "square"
    }

    with open(json_path, 'r') as f:
        cluster_results = json.load(f)

    for entry in cluster_results:
        filename = entry["image"]
        cluster_id = entry["cluster"]
        label = cluster_label_map[cluster_id]

        target_folder = os.path.join(target_root, label)
        os.makedirs(target_folder, exist_ok=True)

        source_path = os.path.join(source_folder, filename)
        target_path = os.path.join(target_folder, filename)

        if os.path.exists(source_path):
            shutil.copy2(source_path, target_path)
        else:
            print(f"⚠️ Missing source image: {source_path}")

    print("✅ All images sorted into folders inside src/data/sorted_images")

# Step 2: Custom preprocessing: CLAHE + Canny edge as 4th channel
def preprocess_image(path):
    img = cv2.imread(path)
    img = cv2.resize(img, (128, 128))

    # CLAHE
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    enhanced = cv2.merge((cl, a, b))
    img_clahe = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    # Add Canny edge map as 4th channel
    gray = cv2.cvtColor(img_clahe, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edges = edges[..., np.newaxis]

    img_clahe = img_clahe.astype(np.float32) / 255.0
    edges = edges.astype(np.float32) / 255.0
    img_4ch = np.concatenate([img_clahe, edges], axis=-1)  # (128, 128, 4)

    return img_4ch

# Step 3: Custom generator to apply the above preprocessing
from tensorflow.keras.utils import Sequence
import random

class CustomImageGenerator(Sequence):
    def __init__(self, filepaths, labels, batch_size=32, shuffle=True):
        self.filepaths = filepaths
        self.labels = labels
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.indices = np.arange(len(filepaths))
        self.on_epoch_end()

    def __len__(self):
        return len(self.filepaths) // self.batch_size

    def __getitem__(self, idx):
        batch_indices = self.indices[idx * self.batch_size:(idx + 1) * self.batch_size]
        batch_imgs = [preprocess_image(self.filepaths[i]) for i in batch_indices]
        batch_labels = [self.labels[i] for i in batch_indices]
        return np.array(batch_imgs), np.array(batch_labels)

    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.indices)

# Step 4: Prepare filepaths + labels
def get_filepaths_and_labels(sorted_dir):
    label_map = {'heart': 0, 'oval': 1, 'round': 2, 'square': 3}
    filepaths, labels = [], []

    for label in os.listdir(sorted_dir):
        full_dir = os.path.join(sorted_dir, label)

        # ✅ Skip .DS_Store or any file that's not a folder
        if not os.path.isdir(full_dir):
            continue

        for fname in os.listdir(full_dir):
            if fname.lower().endswith((".jpg", ".jpeg", ".png")):
                filepaths.append(os.path.join(full_dir, fname))
                labels.append(label_map[label])

    # One-hot encode
    from tensorflow.keras.utils import to_categorical
    labels = to_categorical(labels, num_classes=4)
    return filepaths, labels


# Step 5: Train CNN
def train_cnn():
    sorted_dir = "src/data/sorted_images"

    filepaths, labels = get_filepaths_and_labels(sorted_dir)

    # Split into train and val
    from sklearn.model_selection import train_test_split
    X_train, X_val, y_train, y_val = train_test_split(filepaths, labels, test_size=0.2, stratify=labels)

    train_gen = CustomImageGenerator(X_train, y_train)
    val_gen = CustomImageGenerator(X_val, y_val, shuffle=False)

    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(128, 128, 4)),
        BatchNormalization(),
        MaxPooling2D(2, 2),
        Dropout(0.25),

        Conv2D(64, (3, 3), activation='relu'),
        BatchNormalization(),
        MaxPooling2D(2, 2),
        Dropout(0.25),

        Conv2D(128, (3, 3), activation='relu'),
        BatchNormalization(),
        MaxPooling2D(2, 2),
        Dropout(0.3),

        Flatten(),
        Dense(256, activation='relu'),
        Dropout(0.4),
        Dense(4, activation='softmax')
    ])

    model.compile(optimizer=Adam(learning_rate=1e-4), loss='categorical_crossentropy', metrics=['accuracy'])

    callbacks = [
        EarlyStopping(patience=5, restore_best_weights=True),
        ModelCheckpoint("models/cnn_best.h5", save_best_only=True)
    ]

    model.fit(train_gen, validation_data=val_gen, epochs=16, callbacks=callbacks)

    model.save("models/cnn_face_shape_model.keras")
    print("✅ CNN model saved in models as cnn_face_shape_model")

if __name__ == "__main__":
    sort_images()
    train_cnn()