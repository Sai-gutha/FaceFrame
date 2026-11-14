import sys
import json
import subprocess
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QCheckBox
)
from src.main import run_faceframe_session

CLIENTS_FILE = os.path.join(os.path.dirname(__file__), "clients.json")

def authenticate(username, password):
    if not os.path.exists(CLIENTS_FILE):
        return False
    with open(CLIENTS_FILE, "r") as f:
        clients = json.load(f)
    for client in clients:
        if client["username"].strip() == username.strip() and client["password"].strip() == password.strip():
            return True
    return False

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FaceFrame Login")
        self.setGeometry(300, 200, 500, 240)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Username
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setMinimumHeight(30)
        username_label.setStyleSheet("color: white;")
        self.username_input.setStyleSheet("background-color: white; color: black;")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        username_layout.setSpacing(15)

        # Password
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(30)
        password_label.setStyleSheet("color: white;")
        self.password_input.setStyleSheet("background-color: white; color: black;")
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        password_layout.setSpacing(15)

        # Show Password Checkbox
        self.show_password_checkbox = QCheckBox("Show Password")
        self.show_password_checkbox.setStyleSheet("color: white;")
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)

        # Login Button
        self.login_button = QPushButton("Login")
        self.login_button.setMinimumHeight(35)
        self.login_button.setStyleSheet("background-color: #004080; color: white; font-weight: bold;")
        self.login_button.clicked.connect(self.handle_login)
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

        # Add widgets to layout with spacing
        layout.addStretch()
        layout.addLayout(username_layout)
        layout.addLayout(password_layout)
        layout.addWidget(self.login_button)

        # Add Show Password button at the bottom
        show_password_layout = QHBoxLayout()
        show_password_layout.addStretch()
        show_password_layout.addWidget(self.show_password_checkbox)
        show_password_layout.addStretch()
        layout.addLayout(show_password_layout)

        layout.addStretch()

        self.setLayout(layout)

    def toggle_password_visibility(self, state):
        if state == 2:  # Checked
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if authenticate(username, password):
            self.close()
            try:
                main_script = os.path.join(os.path.dirname(__file__), "main.py")
                if not os.path.exists(main_script):
                    main_script = os.path.join(os.path.dirname(__file__), "glasses-fit-detector", "main.py")
                    if not os.path.exists(main_script):
                        main_script = os.path.join(os.path.dirname(__file__), "glasses-fit-detector", "main.py")
                subprocess.Popen([sys.executable, os.path.abspath(main_script)])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to start FaceFrame session:\n{e}")
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())