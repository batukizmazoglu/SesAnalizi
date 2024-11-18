from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import sounddevice as sd
import wave
from utils.styles import COLORS
from tabs.components import StyledButton

class RecordingTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.audio_data = None  # Mikrofon veya dosya verileri için depolama

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Kayıt kontrolleri
        controls_layout = QHBoxLayout()
        self.record_button = StyledButton("🎤 Kayıt Başlat", COLORS['success'])
        self.stop_button = StyledButton("⏹ Kayıt Durdur", COLORS['error'])
        self.load_button = StyledButton("📂 Ses Yükle", COLORS['primary'])
        self.stop_button.setEnabled(False)
        controls_layout.addWidget(self.record_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(self.load_button)
        layout.addLayout(controls_layout)

        # Grafik için matplotlib figure
        plt.style.use('bmh')
        self.figure, (self.ax_oscillogram, self.ax_spectrogram) = plt.subplots(2, 1, figsize=(8, 6), facecolor=COLORS['background'])
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Sinyal bağlantıları
        self.record_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        self.load_button.clicked.connect(self.load_audio_file)

    def start_recording(self):
        self.record_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.audio_data = []  # Yeni bir kayıt başlatıldığında sıfırlanır
        self.stream = sd.InputStream(callback=self.audio_callback)
        self.stream.start()

    def audio_callback(self, indata, frames, time, status):
        self.audio_data.extend(indata[:, 0])  # İlk kanalın verilerini sakla

    def stop_recording(self):
        self.record_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.stream.stop()
        self.stream.close()
        self.plot_graphs(np.array(self.audio_data))

    def load_audio_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Ses Dosyası Yükle", "", "Ses Dosyaları (*.wav *.mp3)")
        if file_path:
            with wave.open(file_path, 'rb') as wf:
                n_frames = wf.getnframes()
                self.audio_data = np.frombuffer(wf.readframes(n_frames), dtype=np.int16)
                self.plot_graphs(self.audio_data)

    def plot_graphs(self, audio_data):
        self.ax_oscillogram.clear()
        self.ax_oscillogram.plot(audio_data, color=COLORS['primary'])
        self.ax_oscillogram.set_title("Oscillogram", color=COLORS['text'])
        self.ax_oscillogram.set_facecolor(COLORS['background'])

        self.ax_spectrogram.clear()
        self.ax_spectrogram.specgram(audio_data, Fs=44100, cmap='viridis')
        self.ax_spectrogram.set_title("Spectrogram", color=COLORS['text'])
        self.ax_spectrogram.set_facecolor(COLORS['background'])

        self.canvas.draw()
