from transformers import pipeline
import speech_recognition as sr
import librosa
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from tabs.components import StyledButton
from utils.styles import COLORS


class EmotionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

        # Hugging Face duygu analizi modeli
        self.sentiment_analysis = pipeline("sentiment-analysis", model="savasy/bert-base-turkish-sentiment-cased")

        # Pozitif ve negatif kelime listeleri
        self.positive_words = [
            "iyi", "güzel", "harika", "muhteşem", "süper", "mükemmel",
            "mutlu", "sevinçli", "heyecanlı", "keyifli", "neşeli",
            "başarılı", "hoş", "sevindirici", "olumlu", "pozitif",
            "şahane", "fevkalade", "parlak", "coşkulu", "umutlu",
            "ilham verici", "sevgi dolu", "huzurlu", "sıcakkanlı",
            "sempatik", "şanslı", "ışıl ışıl", "nefis", "motive edici",
            "hayranlık uyandıran", "büyüleyici", "aşırı güzel", "tatmin edici",
            "anlamlı", "nezaketli", "cömert", "huzur verici", "şenlikli",
            "dostane", "büyüleyici", "muhteşem", "saf", "canlı", "umut verici"
        ]

        self.negative_words = [
            "kötü", "berbat", "korkunç", "üzgün", "mutsuz", "kızgın",
            "sinirli", "endişeli", "kaygılı", "başarısız", "olumsuz",
            "negatif", "çirkin", "kötümser", "moral", "bozuk", "berbat",
            "ağır", "karmakarışık", "can sıkıcı", "üzücü", "umutsuz",
            "karamsar", "iğrenç", "rahatsız", "nefret dolu", "bıkkın",
            "bunalımlı", "huzursuz", "sert", "acı", "zehirli",
            "kuşkulu", "yıpratıcı", "öfke dolu", "hırçın", "sert",
            "karışık", "üzüntülü", "acımasız", "yıkıcı", "sıkıcı",
            "soğuk", "baskıcı", "zayıf", "çıkmazda", "hüzünlü",
            "şüpheli", "kasvetli", "sıkıntılı", "yetersiz", "zalim"
        ]

        # Olumsuzluk belirten ifadeler
        self.negative_indicators = [
            "değil", "yok", "olmaz", "olmadı", "olmayacak", "asla",
            "hiç", "kesinlikle", "maalesef", "ne yazık ki"
        ]

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Text Edit: Kullanıcıdan metin almak için
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlaceholderText("Duygu analizini yapmak için metni buraya yazın...")
        layout.addWidget(self.text_edit)

        # Metinden duygu analizi butonu
        self.analyze_button = StyledButton("Duygu Analizi Yap", COLORS['primary'])
        self.analyze_button.clicked.connect(self.analyze_sentiment)
        layout.addWidget(self.analyze_button)

        # Ses analizi butonu
        self.record_button = StyledButton("Ses Kaydını Duygu İçin Analiz Et", COLORS['success'])
        self.record_button.clicked.connect(self.analyze_audio_emotion)
        layout.addWidget(self.record_button)

        # Sonuçlar: Duygu analizinin sonuçları burada gösterilecek
        self.result_label = QLabel("Sonuç: ", self)
        layout.addWidget(self.result_label)

        # Grafik Alanı: Sonuçları görselleştirecek alan
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def analyze_text_sentiment(self, text):
        """Metni analiz eder ve duygu durumunu belirler"""
        text = text.lower()

        # Pozitif ve negatif kelime sayılarını hesapla
        positive_count = sum(1 for word in self.positive_words if word in text)
        negative_count = sum(1 for word in self.negative_words if word in text)

        # Olumsuzluk kontrolü
        has_negation = any(neg in text for neg in self.negative_indicators)

        # Metindeki toplam kelime sayısını hesapla
        word_count = len(text.split())

        # Uzun metinlerde nötr etkisi artır
        if word_count > 15:
            neutral_boost = 0.2
            positive_count *= 0.8
            negative_count *= 0.8
        else:
            neutral_boost = 0.0

        # Olumsuzluk ifadeleri bağlamında analiz
        if has_negation:
            if positive_count > 0 and negative_count == 0:
                return "NEGATIVE", {"POSITIVE": 0.1, "NEGATIVE": 0.9, "NEUTRAL": 0.0}
            elif negative_count > 0 and positive_count == 0:
                return "POSITIVE", {"POSITIVE": 0.8, "NEGATIVE": 0.1, "NEUTRAL": 0.1}
            elif positive_count > 0 and negative_count > 0:
                return "NEGATIVE", {"POSITIVE": 0.1, "NEGATIVE": 0.8, "NEUTRAL": 0.1}

        # Eğer pozitif kelime varsa ve negatif kelime yoksa pozitif değerlendir
        if positive_count > 0 and negative_count == 0:
            return "POSITIVE", {"POSITIVE": 0.9 - neutral_boost, "NEGATIVE": 0.05, "NEUTRAL": 0.05 + neutral_boost}

        # Eğer negatif kelime varsa ve pozitif kelime yoksa negatif değerlendir
        if negative_count > 0 and positive_count == 0:
            return "NEGATIVE", {"POSITIVE": 0.05, "NEGATIVE": 0.9 - neutral_boost, "NEUTRAL": 0.05 + neutral_boost}

        # Eğer pozitif kelime sayısı negatiften fazlaysa
        if positive_count > negative_count:
            return "POSITIVE", {"POSITIVE": 0.7, "NEGATIVE": 0.1, "NEUTRAL": 0.2 + neutral_boost}
        # Eğer negatif kelime sayısı pozitiften fazlaysa
        elif negative_count > positive_count:
            return "NEGATIVE", {"POSITIVE": 0.1, "NEGATIVE": 0.7, "NEUTRAL": 0.2 + neutral_boost}
        # Eğer her ikisi de eşitse, nötr değerlendir
        elif positive_count == negative_count:
            return "NEUTRAL", {"POSITIVE": 0.3, "NEGATIVE": 0.3, "NEUTRAL": 0.4 + neutral_boost}

        # Hiç pozitif veya negatif kelime yoksa nötr kabul et
        return "NEUTRAL", {"POSITIVE": 0.1, "NEGATIVE": 0.1, "NEUTRAL": 0.8 + neutral_boost}

    def analyze_sentiment(self):
        text = self.text_edit.toPlainText()

        try:
            # Önce kendi analiz sistemimizi kullan
            label, scores = self.analyze_text_sentiment(text)

            # Eğer sonuç alamazsak modeli kullan
            if label is None:
                result = self.sentiment_analysis(text)
                sentiment = result[0]
                label = sentiment['label']
                score = sentiment['score']
                # Skorları nötr eşiklerine göre ayarla
                scores = {
                    "POSITIVE": score if label == "POSITIVE" and score > 0.6 else 0.1,
                    "NEGATIVE": score if label == "NEGATIVE" and score > 0.6 else 0.1,
                    "NEUTRAL": score if label == "NEUTRAL" or score <= 0.6 else 0.8
                }

            # Sonuçları yazdır ve çiz
            sentiment_text = f"Sonuç: {label} ({max(scores.values()):.2f})"
            self.result_label.setText(sentiment_text)
            self.plot_sentiment(scores)

        except Exception as e:
            self.result_label.setText(f"Hata: {str(e)}")

    def analyze_audio_emotion(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.result_label.setText("Konuşun, ses kaydediliyor...")
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio, language="tr-TR")
                self.text_edit.setPlainText(text)
                self.analyze_sentiment()
            except sr.UnknownValueError:
                self.result_label.setText("Ses anlaşılamadı.")
            except sr.RequestError as e:
                self.result_label.setText(f"Google API hizmetine ulaşılamıyor: {e}")
            except Exception as e:
                self.result_label.setText(f"Hata: {str(e)}")

    def plot_sentiment(self, scores):
        # Bar grafiği oluştur
        self.ax.clear()
        colors = [COLORS['success'], COLORS['error'], COLORS['warning']]
        self.ax.bar(scores.keys(), scores.values(), color=colors)

        # Başlık ve etiketler
        self.ax.set_title("Duygu Analizi Sonucu", color=COLORS['text'])
        self.ax.set_ylabel("Skor", color=COLORS['text'])
        self.ax.set_ylim(0, 1)

        # Grafiği güncelle
        self.canvas.draw()


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow

    app = QApplication([])
    main_window = QMainWindow()
    tab = EmotionTab()
    main_window.setCentralWidget(tab)
    main_window.setWindowTitle("Duygu Analizi Uygulaması")
    main_window.show()
    app.exec_()
