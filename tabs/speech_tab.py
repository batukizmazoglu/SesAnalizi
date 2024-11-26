import sys
import speech_recognition as sr
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal

class SpeechRecognitionThread(QThread):
    """
    Arka planda çalışan ses tanıma iş parçacığı.
    """
    text_signal = pyqtSignal(str)
    word_count_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = True
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.word_count = 0

    def run(self):
        try:
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source)  # Arka plan gürültüsünü ayarla
                while self.running:
                    try:
                        # Mikrofonu dinle
                        audio = self.recognizer.listen(source, timeout=5)

                        # Speech-to-text
                        text = self.recognizer.recognize_google(audio, language="tr-TR")
                        self.word_count += len(text.split())

                        # Sinyalleri gönder
                        self.text_signal.emit(text)
                        self.word_count_signal.emit(self.word_count)

                    except sr.UnknownValueError:
                        self.text_signal.emit("Anlaşılamadı, tekrar deneyin.")
                    except sr.RequestError as e:
                        self.text_signal.emit(f"API hatası: {e}")
                    except Exception as e:
                        self.text_signal.emit(f"Beklenmeyen hata: {e}")

        except Exception as e:
            self.text_signal.emit(f"Başlatma hatası: {e}")

    def stop(self):
        self.running = False


class SpeechTab(QWidget):
    """
    PyQt5 arayüzü ile ses tanıma ve kelime sayma sekmesi.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.thread = None

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Başlık
        self.title = QLabel("Konuşma Analizi")
        self.title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2;")
        layout.addWidget(self.title)

        # Konuşma Metni
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setPlaceholderText("Konuşulan metin burada görünecek...")
        layout.addWidget(self.text_area)

        # Kelime Sayısı Gösterimi
        self.word_count_label = QLabel("Toplam Kelime Sayısı: 0")
        self.word_count_label.setStyleSheet("font-size: 14px; color: #424242;")
        layout.addWidget(self.word_count_label)

        # Başlat ve Durdur Düğmeleri
        self.start_button = QPushButton("Başlat")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #A5D6A7;  /* Açık yeşil */
                color: white;  /* Yazı rengi beyaz */
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #81C784;  /* Hafif koyulaşan yeşil hover rengi */
            }
            QPushButton:pressed {
                background-color: #66BB6A;  /* Daha koyu yeşil pressed rengi */
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        self.start_button.clicked.connect(self.start_recognition)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Durdur")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #A5D6A7;  /* Açık yeşil */
                color: white;  /* Yazı rengi beyaz */
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #81C784;  /* Hafif koyulaşan yeşil hover rengi */
            }
            QPushButton:pressed {
                background-color: #66BB6A;  /* Daha koyu yeşil pressed rengi */
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        self.stop_button.clicked.connect(self.stop_recognition)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

    def start_recognition(self):
        if self.thread is None or not self.thread.isRunning():
            self.thread = SpeechRecognitionThread()
            self.thread.text_signal.connect(self.update_text_area)
            self.thread.word_count_signal.connect(self.update_word_count)
            self.thread.start()

            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)

    def stop_recognition(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()

            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def update_text_area(self, text):
        """
        Gelen konuşma metnini metin alanına ekler.
        """
        self.text_area.append(text)

    def update_word_count(self, count):
        """
        Kelime sayısını günceller.
        """
        self.word_count_label.setText(f"Toplam Kelime Sayısı: {count}")

    def closeEvent(self, event):
        """
        Sekme kapatıldığında thread'i durdurur.
        """
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
        event.accept()
