from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from settings_manager import save_settings
from datetime import date 


class SetupWizard(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)

        self.settings = settings or {}
        self.step = 0

        self.setWindowTitle("ResearchEngine Setup Wizard")
        self.setFixedSize(600, 400)
        self.setWindowModality(Qt.ApplicationModal)

        # ===== MAIN LAYOUT =====
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.render_step()

    # ================= CLEAR LAYOUT (SAFE) =================
    def clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)

            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

            child_layout = item.layout()
            if child_layout is not None:
                self.clear_sub_layout(child_layout)

    def clear_sub_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)

            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

            if item.layout() is not None:
                self.clear_sub_layout(item.layout())

    # ================= RENDER =================
    def render_step(self):
        self.clear_layout()

        if self.step == 0:
            self.step_welcome()
        elif self.step == 1:
            self.step_api()
        elif self.step == 2:
            self.step_preferences()
        elif self.step == 3:
            self.step_finish()

    # ================= STEP 1 =================
    def step_welcome(self):
        title = QLabel("Welcome to ResearchEngine")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        currentYear = date.today().year

        subtitle = QLabel(f"{currentYear} © Proton Technologies - All rights reserved")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: gray;")

        btn = QPushButton("Get Started →")
        btn.clicked.connect(self.next_step)

        self.layout.addStretch()
        self.layout.addWidget(title)
        self.layout.addWidget(subtitle)
        self.layout.addWidget(btn, alignment=Qt.AlignCenter)
        self.layout.addStretch()

    # ================= STEP 2 =================
    def step_api(self):
        title = QLabel("Enter YouTube API Key")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("Paste your API key here...")

        guide = QPushButton("How to get API key")
        guide.clicked.connect(self.open_guide)

        btn = QPushButton("Continue →")
        btn.clicked.connect(self.save_api)

        self.layout.addStretch()
        self.layout.addWidget(title)
        self.layout.addWidget(self.api_input)
        self.layout.addWidget(guide, alignment=Qt.AlignCenter)
        self.layout.addWidget(btn, alignment=Qt.AlignCenter)
        self.layout.addStretch()

    def open_guide(self):
        import webbrowser
        webbrowser.open("https://console.cloud.google.com/")

    def save_api(self):
        key = self.api_input.text().strip()

        if not key:
            QMessageBox.warning(self, "Error", "API key required")
            return

        self.settings["api_key"] = key
        save_settings(self.settings)

        self.next_step()

    # ================= STEP 3 =================
    def step_preferences(self):
        title = QLabel("⚙ Preferences")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.max_results = QLineEdit()
        self.max_results.setText("20")

        label = QLabel("Max videos per research")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: gray;")

        btn = QPushButton("Continue →")
        btn.clicked.connect(self.save_preferences)

        self.layout.addStretch()
        self.layout.addWidget(title)
        self.layout.addWidget(self.max_results)
        self.layout.addWidget(label)
        self.layout.addWidget(btn, alignment=Qt.AlignCenter)
        self.layout.addStretch()

    def save_preferences(self):
        try:
            self.settings["max_results"] = int(self.max_results.text())
        except:
            self.settings["max_results"] = 20

        save_settings(self.settings)
        self.next_step()

    # ================= STEP 4 =================
    def step_finish(self):
        title = QLabel("Setup Complete")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("You're ready to use ResearchEngine")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: gray;")

        btn = QPushButton("Launch App")
        btn.clicked.connect(self.finish)

        self.layout.addStretch()
        self.layout.addWidget(title)
        self.layout.addWidget(subtitle)
        self.layout.addWidget(btn, alignment=Qt.AlignCenter)
        self.layout.addStretch()

    def finish(self):
        self.accept()

    # ================= NAVIGATION =================
    def next_step(self):
        self.step += 1
        self.render_step()