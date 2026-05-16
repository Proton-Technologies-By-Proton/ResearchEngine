import sys, os
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from collector import collect_videos
from analyzer import analyze_videos_with_custom
from trends import fetch_trends_data
from insight_engine_v3 import generate_full_insights
from exporter import export_to_csv
from settings_manager import load_settings, save_settings
from setup_wizard import SetupWizard


settings = load_settings()


# ===== BACKGROUND =====
class GradientBackground(QWidget):
    def __init__(self):
        super().__init__()
        self.shift = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(60)

    def animate(self):
        self.shift += 1
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        grad = QLinearGradient(
            self.shift, 0,
            self.width() + self.shift, self.height()
        )
        grad.setColorAt(0, QColor(15, 18, 25))
        grad.setColorAt(0.5, QColor(10, 12, 18))
        grad.setColorAt(1, QColor(15, 18, 25))
        p.fillRect(self.rect(), grad)


# ===== CARD =====
class Card(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
        QFrame {
            background: rgba(255,255,255,0.05);
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.08);
        }
        """)


# ===== KPI =====
class KPICard(Card):
    def __init__(self, title):
        super().__init__()
        layout = QVBoxLayout()

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color:#9ca3af; font-size:12px;")

        self.value = QLabel("--")
        self.value.setFont(QFont("Segoe UI", 20, QFont.Bold))

        layout.addWidget(title_lbl)
        layout.addWidget(self.value)
        self.setLayout(layout)


# ===== CHART =====
class Chart(FigureCanvasQTAgg):
    def __init__(self):
        self.fig = Figure(facecolor="#0d1117")
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.ax.tick_params(colors='white')

    def update_chart(self, data):
        self.ax.clear()
        if not data:
            self.draw()
            return

        labels = [k for k, v in data]
        values = [v for k, v in data]

        bars = self.ax.bar(labels, values)
        for bar in bars:
            bar.set_alpha(0.85)

        self.draw()


# ===== SETTINGS =====
class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ResearchEngine System Settings")
        self.setFixedSize(360, 200)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout()

        title = QLabel("API Key")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))

        self.api = QLineEdit()
        self.api.setText(settings.get("api_key", ""))

        save = QPushButton("Save")
        save.clicked.connect(self.save)

        layout.addWidget(title)
        layout.addWidget(self.api)
        layout.addWidget(save)

        self.setLayout(layout)

    def save(self):
        settings["api_key"] = self.api.text().strip()
        save_settings(settings)
        self.close()


# ===== MAIN UI =====
class ProtonUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ResearchEngine v0.3.0 Alpha")
        self.resize(1400, 800)

        self.settings_window = None

        self.bg = GradientBackground()
        self.setCentralWidget(self.bg)

        self.setFont(QFont("Segoe UI", 10))

        self.build_ui()

    def build_ui(self):
        layout = QHBoxLayout(self.bg)

        # ===== SIDEBAR =====
        side = QVBoxLayout()

        logo = QLabel("ResearchEngine")
        logo.setFont(QFont("Segoe UI", 20, QFont.Bold))
        side.addWidget(logo)

        self.tabs = QStackedWidget()

        for name, i in [("Dashboard", 0), ("Results", 1), ("Insights", 2)]:
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, x=i: self.tabs.setCurrentIndex(x))
            side.addWidget(btn)

        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.open_settings)

        side.addWidget(settings_btn)
        side.addStretch()

        layout.addLayout(side, 1)

        # ===== MAIN =====
        container = QVBoxLayout()
        container.setSpacing(15)

        container.addWidget(self.tabs)
        layout.addLayout(container, 4)

        self.build_dashboard()
        self.build_results()
        self.build_insights()

    # ===== DASHBOARD =====
    def build_dashboard(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        self.topic = QLineEdit()
        self.topic.setPlaceholderText("Enter research topic")

        self.criteria = QLineEdit()
        self.criteria.setPlaceholderText("Criteria (optional)")

        run = QPushButton("Run Research")
        run.clicked.connect(self.run)

        layout.addWidget(self.topic)
        layout.addWidget(self.criteria)
        layout.addWidget(run)

        row = QHBoxLayout()
        self.k1 = KPICard("Attention")
        self.k2 = KPICard("Videos")
        self.k3 = KPICard("Trend")

        row.addWidget(self.k1)
        row.addWidget(self.k2)
        row.addWidget(self.k3)

        layout.addLayout(row)

        self.chart = Chart()
        layout.addWidget(self.chart)

        self.status = QLabel("Ready")
        self.status.setStyleSheet("color:#00ffa6;")

        layout.addWidget(self.status)

        self.tabs.addWidget(page)

    # ===== RESULTS =====
    def build_results(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        layout.addWidget(self.table)

        btn = QPushButton("Open CSV")
        btn.clicked.connect(self.open_csv)

        layout.addWidget(btn)

        self.tabs.addWidget(page)

    def open_csv(self):
        path = "REexports/REoutput.csv"
        if os.path.exists(path):
            os.startfile(path)

    # ===== INSIGHTS =====
    def build_insights(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        self.insight = QTextEdit()
        self.insight.setReadOnly(True)

        layout.addWidget(self.insight)

        self.tabs.addWidget(page)

    # ===== SETTINGS =====
    def open_settings(self):
        if self.settings_window and self.settings_window.isVisible():
            self.settings_window.activateWindow()
            return

        self.settings_window = SettingsWindow()
        self.settings_window.show()

    # ===== RUN =====
    def run(self):
        topic = self.topic.text().strip()

        if not topic:
            self.status.setText("Enter topic")
            return

        api = settings.get("api_key")
        if not api:
            self.status.setText("Set API key")
            return

        criteria = {c: [c] for c in self.criteria.text().split(",") if c}

        self.status.setText("Running...")

        try:
            videos = collect_videos(topic, api)

            analyzed, dynamic_keywords = analyze_videos_with_custom(videos, criteria)

            trends = fetch_trends_data(topic)

            insights = generate_full_insights(
                analyzed, trends, criteria, dynamic_keywords
            )

            export_to_csv(analyzed)

            self.update_ui(analyzed, insights)

            self.status.setText("Done")

        except Exception as e:
            self.status.setText(str(e))

    # ===== UPDATE UI =====
    def update_ui(self, v, ins):
        self.k1.value.setText(str(sum(int(x.get("Views", 0)) for x in v)))
        self.k2.value.setText(str(len(v)))
        self.k3.value.setText(ins.get("trends", "-"))

        self.chart.update_chart(ins.get("youtube", {}).get("top_keywords", []))

        text = "\n".join(ins.get("summary", [])) + "\n\n" + ins.get("opportunity", "")
        self.insight.setText(text)

        if not v:
            return

        self.table.setRowCount(len(v))
        self.table.setColumnCount(len(v[0].keys()))
        self.table.setHorizontalHeaderLabels(list(v[0].keys()))

        for r, row in enumerate(v):
            for c, k in enumerate(row.keys()):
                self.table.setItem(r, c, QTableWidgetItem(str(row.get(k, ""))))


# ===== ENTRY POINT =====
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # ===== SETUP FIRST =====
    if not settings.get("api_key"):
        wizard = SetupWizard(None, settings)
        wizard.exec()

    # ===== MAIN UI =====
    win = ProtonUI()
    win.show()

    sys.exit(app.exec())
