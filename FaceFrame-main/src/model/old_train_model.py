import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Load data
df = pd.read_csv('face_shape_data.csv', header=None)

X = df.iloc[:, :-1]  # landmark coordinates
y = df.iloc[:, -1]   # face shape labels

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train classifier
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Evaluate
print(f"Accuracy: {model.score(X_test, y_test):.2f}")

# Save model
joblib.dump(model, "face_shape_model.pkl")
print("[SAVED] face_shape_model.pkl")