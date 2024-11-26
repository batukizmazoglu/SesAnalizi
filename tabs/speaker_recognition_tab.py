import sys
import os
import librosa
import numpy as np
import sounddevice as sd
import wave
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel, QPushButton, QTextEdit
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from PyQt5.QtCore import Qt
import os

dataset_path = 'C:\\Users\\user\\PycharmProjects\\SesAnalizi\\ses_kayitlari'


class SpeakerRecognitionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.model = RandomForestClassifier()  # Modeli başlatıyoruz

    def init_ui(self):
        layout = QVBoxLayout()

        # Başlık
        title = QLabel("🎤 Ses Tanıma Modeli ve Metrikler")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2;")
        layout.addWidget(title)

        # Sonuç metin alanı
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        layout.addWidget(self.result_area)

        # Modeli eğitme butonu
        train_button = QPushButton("Modeli Eğit ve Sonuçları Göster")
        train_button.clicked.connect(self.train_model)
        layout.addWidget(train_button)

        # Ses kaydetme butonu
        record_button = QPushButton("Ses Kaydet ve Tahmin Et")
        record_button.clicked.connect(self.record_and_predict)
        layout.addWidget(record_button)

        self.setLayout(layout)

    def prepare_training_data(self):
        X = []
        y = []
        speaker_labels = {'Kisi1': 0, 'Kisi2': 1}  # Konuşmacı etiketleri

        for speaker, label in speaker_labels.items():
            speaker_folder = os.path.join(dataset_path, speaker)
            if os.path.exists(speaker_folder):
                for file in os.listdir(speaker_folder):
                    if file.endswith('.wav'):
                        file_path = os.path.join(speaker_folder, file)
                        try:
                            # Ses dosyasını yükleyin ve MFCC özelliklerini çıkarın
                            audio, sr = librosa.load(file_path, sr=None, mono=True)
                            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)  # MFCC'yi daha tutarlı çıkaralım
                            mfcc = np.mean(mfcc.T, axis=0)  # MFCC'yi ortalama alarak sabitleyin

                            X.append(mfcc)
                            y.append(label)
                        except Exception as e:
                            print(f"Hata: {file_path} dosyasında problem oluştu - {e}")
            else:
                print(f"{speaker_folder} dizini bulunamadı!")

        return np.array(X), np.array(y)

    def train_model(self):
        try:
            X_train, y_train = self.prepare_training_data()

            # Modeli oluşturun ve eğitin
            self.model.fit(X_train, y_train)

            # Sonuçları gösterme
            self.result_area.setText("Model eğitildi başarıyla!")

        except FileNotFoundError as e:
            self.result_area.setText(str(e))
        except Exception as e:
            self.result_area.setText(f"Beklenmedik bir hata oluştu: {e}")

    def record_and_predict(self):
        # Ses kaydetme işlemi
        fs = 16000  # Ses örnekleme frekansı
        duration = 3  # Kayıt süresi (3 saniye)
        self.result_area.setText("Ses kaydediliyor...")

        # Kaydı başlat
        audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
        sd.wait()  # Kayıt bitene kadar bekle

        # Ses kaydını dosyaya kaydet
        self.save_audio(audio_data, fs, "test_recording.wav")

        # Ses kaydını yükleyip tahmin etme
        predicted_speaker = self.predict_speaker_from_file("test_recording.wav")

        # Sonucu kullanıcıya göster
        self.result_area.setText(f"Konuşmacı Tahmini: {predicted_speaker}")

    def save_audio(self, audio_data, fs, filename):
        # Kayıt edilen ses verisini dosyaya kaydetme
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(audio_data.tobytes())

    def predict_speaker_from_file(self, audio_file):
        # Kaydedilen ses dosyasından özellik çıkarma ve tahmin yapma
        try:
            audio, sr = librosa.load(audio_file, sr=None, mono=True)
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)  # MFCC özelliklerini çıkar
            mfcc = np.mean(mfcc.T, axis=0)  # Özellik çıkarımı

            # Tahmin yap
            predicted_speaker = self.model.predict([mfcc])
            return "Kisi1" if predicted_speaker[0] == 0 else "Kisi2"
        except Exception as e:
            self.result_area.setText(f"Hata: {e}")
            return "Hata"


class VoiceAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ses Analizi Uygulaması")
        self.setGeometry(100, 100, 1280, 720)

        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Başlık
        title = QLabel("Ses Analizi ve Duygu Tanıma Sistemi")
        title.setStyleSheet("""
            QLabel {
                color: #1976D2;
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        layout.addWidget(title, alignment=Qt.AlignCenter)

        # Tab widget oluşturma
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Tüm tabları ekleme
        tabs.addTab(SpeakerRecognitionTab(), "👤 Konuşmacı Tanıma")


# Ana fonksiyon
def main():
    app = QApplication(sys.argv)

    # Uygulama penceresini başlat
    window = VoiceAnalysisApp()
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
