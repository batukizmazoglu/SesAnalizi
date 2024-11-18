from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

from utils.styles import COLORS
from tabs.components import StyledButton

class RecordingTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Kayıt kontrolleri
        controls_layout = QHBoxLayout()
        self.record_button = StyledButton("🎤 Kayıt Başlat", COLORS['success'])
        self.stop_button = StyledButton("⏹ Kayıt Durdur", COLORS['error'])
        self.stop_button.setEnabled(False)
        controls_layout.addWidget(self.record_button)
        controls_layout.addWidget(self.stop_button)
        layout.addLayout(controls_layout)

        # Histogram için matplotlib figure
        plt.style.use('bmh')
        self.figure, self.ax = plt.subplots(facecolor=COLORS['background'])
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Sinyal bağlantıları
        self.record_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)

    def start_recording(self):
        self.record_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        # Ses kaydı başlatma kodu

    def stop_recording(self):
        self.record_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        #Ses kaydı durdurma ve analiz başlatma kodu

    def update_histogram(self, audio_data):
        self.ax.clear()
        self.ax.hist(audio_data, bins=50, color=COLORS['primary'])
        self.ax.set_facecolor(COLORS['background'])
        self.canvas.draw()