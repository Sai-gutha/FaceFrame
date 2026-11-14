# FaceFrame 👓

FaceFrame is an AI-powered virtual glasses try-on and face-shape detection system using real-time computer vision, MediaPipe, and machine learning.

---

## 📁 Project Structure

```
FaceFrame/
├── glasses-fit-detector/
│   ├── main.py
│   ├── models/
│   ├── glasses/
│   ├── training_samples/
│   └── face_shape_data.csv
├── login_screen.py
├── run.py
├── requirements.md
├── README.md
├── .gitignore
└── logs/ (add to .gitignore)
```

---

## 📦 Requirements

Install the dependencies using pip:
```bash
pip install -r requirements.txt
```

If needed, generate the list from your environment:
```bash
pip freeze > requirements.txt
```

---

## 🧠 ML Assets

- `models/face_shape_model.pkl` - Pretrained model
- `glasses/` - PNG overlays for glasses by face shape
- `training_samples/` - Sample face shapes for reference

---

## 🚀 Running FaceFrame

Start the app:
```bash
python3 glasses-fit-detector/login_screen.py 
```

Replace `<your_username>` with a user listed in `clients.json`.

---

## 🧪 Testing Locally

Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

Then install dependencies and run:
```bash
pip install -r requirements.txt
python glasses-fit-detector/main.py
python glasses-fit-detector/login_screen.py (if you want to go through customer panel (username and password in clients.json))
```

---

## ❌ .gitignore

Make sure to exclude temporary or sensitive files:
```
__pycache__/
*.pyc
logs/
*.log
.env
.DS_Store
```

## 📦 Deployment Notes

Make sure all assets and models are pushed to GitHub, and include:

- `requirements.txt`
- `README.md`
- All image/model assets needed to run

---

## 📊 Model Diagnostics

For current notes on validation accuracy reliability, dataset risks, and future improvements needed before production startup use, see [`docs/model_diagnostics.md`](docs/model_diagnostics.md).

## 🧑‍💻 Contributors

- Rishi Singhvi — Founder & Engineer
- Parv Singhal - Founding ML Engineer

---

FaceFrame © 2025. All rights reserved.
