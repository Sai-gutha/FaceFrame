
# FaceFrame Dependency Requirements

This document lists all the core libraries and dependencies used in the FaceFrame project, grouped by functionality.

---

## Core Dependencies

| Library     | Purpose                              | Version (Recommended) |
|-------------|--------------------------------------|------------------------|
| Python      | Programming Language                 | >=3.10                 |
| OpenCV      | Real-time computer vision            | opencv-python >= 4.5   |
| MediaPipe   | Face and mesh landmark detection     | mediapipe >= 0.10.0    |
| NumPy       | Numerical operations                 | numpy >= 1.20          |
| Pandas      | Data processing (training/logging)   | pandas >= 1.3          |
| scikit-learn| Model training and evaluation        | scikit-learn >= 0.24   |
| joblib      | Model persistence                    | joblib >= 1.1          |

---

## Optional / Extended Dependencies

| Library        | Purpose                                  | Version            |
|----------------|------------------------------------------|--------------------|
| pyinstaller    | Packaging into standalone executables     | latest             |
| pyzbar         | QR code reading (future use)              | optional           |
| flask / fastapi| Backend API (planned future expansion)    | optional           |

---

## System Requirements

- macOS / Windows / Linux with camera support
- Python 3.10+ installed via pyenv or system package manager
- Sufficient permissions for webcam usage and file I/O

---

## Installation Command

```bash
pip install opencv-python mediapipe numpy pandas scikit-learn joblib
```

---

For contributions, please use a virtual environment and install packages using:

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```
