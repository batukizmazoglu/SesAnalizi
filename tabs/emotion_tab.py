from transformers import pipeline
import speech_recognition as sr
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QApplication, QMainWindow
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class EmotionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        # Hugging Face duygu analizi modeli
        self.sentiment_analysis = pipeline("sentiment-analysis", model="savasy/bert-base-turkish-sentiment-cased")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Text Edit: Kullanıcıdan metin almak için
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlaceholderText("Duygu analizini yapmak için metni buraya yazın...")
        layout.addWidget(self.text_edit)

        # Button: Duygu analizi başlatma butonu
        self.analyze_button = QPushButton("Duygu Analizini Yap", self)
        self.analyze_button.clicked.connect(self.analyze_sentiment)
        layout.addWidget(self.analyze_button)

        # Ses kaydı butonu
        self.record_button = QPushButton("Sesli Konuşmayı Kaydet", self)
        self.record_button.clicked.connect(self.record_audio)
        layout.addWidget(self.record_button)

        # Sonuçlar: Duygu analizinin sonuçları burada gösterilecek
        self.result_label = QLabel("Sonuç: ", self)
        layout.addWidget(self.result_label)

        # Grafik Alanı: Sonuçları görselleştirecek alan
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def record_audio(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Ses kaydediliyor... Konuşun.")
            audio = recognizer.listen(source)
            print("Ses kaydı alındı.")

        try:
            print("Metne dönüştürülüyor...")
            # Ses kaydını metne dönüştürme
            text = recognizer.recognize_google(audio, language="tr-TR")
            print(f"Dönüştürülen metin: {text}")
            self.text_edit.setPlainText(text)  # Metni QTextEdit'e yerleştir
            self.analyze_sentiment()  # Duygu analizi yap
        except sr.UnknownValueError:
            print("Ses anlaşılamadı.")
        except sr.RequestError:
            print("Google API hizmetine ulaşılamıyor.")

    def analyze_sentiment(self):
        # Kullanıcıdan metni al
        text = self.text_edit.toPlainText()

        try:
            # Hugging Face ile duygu analizi yap
            result = self.sentiment_analysis(text)

            # Birden fazla duygu tahmini yapılabilir, bu nedenle tüm sonuçları değerlendiriyoruz
            scores = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}

            for sentiment in result:
                label = sentiment['label']
                score = sentiment['score']
                if label == "POSITIVE":
                    scores["POSITIVE"] += score
                elif label == "NEGATIVE":
                    scores["NEGATIVE"] += score

            # Nötr skoru belirleme
            scores["NEUTRAL"] = max(0, 1 - scores["POSITIVE"] - scores["NEGATIVE"])

            # Sonuçları yazdır
            sentiment_text = f"Sonuçlar: POSITIVE ({scores['POSITIVE']:.2f}), NEGATIVE ({scores['NEGATIVE']:.2f}), NEUTRAL ({scores['NEUTRAL']:.2f})"
            self.result_label.setText(sentiment_text)

            # Sonuçları görselleştirme
            self.plot_sentiment(scores)

        except Exception as e:
            self.result_label.setText(f"Hata: {str(e)}")

    def plot_sentiment(self, scores):
        # Bar grafiği oluştur
        self.ax.clear()
        colors = ['green', 'red', 'gray']
        self.ax.bar(scores.keys(), scores.values(), color=colors)

        # Başlık ve etiketler
        self.ax.set_title("Duygu Analizi Sonucu")
        self.ax.set_ylabel("Skor")
        self.ax.set_ylim(0, 1)

        # Grafiği güncelle
        self.canvas.draw()

# PyQt5 uygulaması başlatma
if __name__ == '__main__':
    app = QApplication([])
    main_window = QMainWindow()
    tab = EmotionTab()
    main_window.setCentralWidget(tab)
    main_window.setWindowTitle("Duygu Analizi Uygulaması")
    main_window.show()
    app.exec_()
