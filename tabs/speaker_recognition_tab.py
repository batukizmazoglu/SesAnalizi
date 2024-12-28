import sys
import os
import librosa
import numpy as np
import sounddevice as sd
import soundfile as sf
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel, QPushButton, QTextEdit
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import confusion_matrix, classification_report
from PyQt5.QtCore import Qt
from sklearn.pipeline import Pipeline
import joblib

# Dataset path
dataset_path = 'C:\\Users\\user\\PycharmProjects\\SesAnalizi\\ses_kayitlari'

class SpeakerRecognitionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.model = None  # Initially no model loaded
        self.label_encoder = None
        self.init_ui()

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

    def preprocess_audio(self, audio, sr):
        # Ses işleme: preemphasis, normalizasyon ve sessizlik kesme
        audio = librosa.effects.preemphasis(audio)
        audio = librosa.util.normalize(audio)
        audio, _ = librosa.effects.trim(audio, top_db=20)
        return audio

    def extract_features(self, audio, sr):
        # Normalize audio
        audio = librosa.util.normalize(audio)

        # Extract MFCC features
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=20)
        mfcc_mean = np.mean(mfcc.T, axis=0)

        # Extract delta and delta-delta features with reduced width
        delta_mfcc = librosa.feature.delta(mfcc, width=5)
        delta2_mfcc = librosa.feature.delta(mfcc, order=2, width=5)

        # Combine all features
        features = np.hstack([
            mfcc_mean,
            np.mean(delta_mfcc.T, axis=0),
            np.mean(delta2_mfcc.T, axis=0)
        ])
        return features

    def prepare_training_data(self):
        X = []
        y = []
        # İki konuşmacı için etiketler
        speaker_labels = {'Kisi1': 0, 'Kisi2': 1}

        for speaker, label in speaker_labels.items():
            speaker_folder = os.path.join(dataset_path, speaker)
            if os.path.exists(speaker_folder):
                for file in os.listdir(speaker_folder):
                    if file.endswith('.wav'):
                        file_path = os.path.join(speaker_folder, file)
                        try:
                            audio, sr = librosa.load(file_path, sr=16000, mono=True)
                            audio = self.preprocess_audio(audio, sr)
                            # Trim sonrası kontrol: 2 saniyeden azsa atla
                            if len(audio) < sr * 2:
                                self.result_area.append(f"Ses dosyası çok kısa: {file_path}")
                                continue
                            features = self.extract_features(audio, sr)
                            X.append(features)
                            y.append(label)
                        except Exception as e:
                            self.result_area.append(f"Error processing {file_path}: {e}")
            else:
                self.result_area.append(f"Directory not found: {speaker_folder}")

        X = np.array(X)
        y = np.array(y)

        if X.size == 0:
            raise ValueError("No features extracted. Check your audio files and feature extraction process.")

        # Eğitim ve test setine ayırma
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        return X_train, X_test, y_train, y_test

    def train_model(self):
        try:
            self.result_area.setText("Veri seti hazırlanıyor...")
            X_train, X_test, y_train, y_test = self.prepare_training_data()
            self.result_area.append(f"Veri seti hazırlandı. Eğitim örnek sayısı: {len(X_train)}, Test örnek sayısı: {len(X_test)}")

            # Model pipeline tanımlama
            pipeline = Pipeline([
                ('scaler', StandardScaler()),  # Özellik ölçeklendirme
                ('classifier', RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42))  # Sınıflandırıcı
            ])

            self.result_area.append("Model eğitiliyor...")

            # Hiperparametre optimizasyonu
            param_grid = {
                'classifier__n_estimators': [100, 200, 300],
                'classifier__max_depth': [None, 10, 20],
                'classifier__min_samples_split': [2, 5, 10]
            }

            grid_search = GridSearchCV(pipeline, param_grid, cv=2, n_jobs=-1, verbose=1)
            grid_search.fit(X_train, y_train)

            self.model = grid_search.best_estimator_
            self.label_encoder = LabelEncoder()
            self.label_encoder.fit(['Kisi1', 'Kisi2'])

            # Sonuçları göster
            self.result_area.append(f"Model eğitildi. En iyi parametreler: {grid_search.best_params_}")
            self.evaluate_model(X_test, y_test)
            self.save_model()

        except Exception as e:
            self.result_area.setText(f"Beklenmeyen hata: {e}")

    def evaluate_model(self, X_test, y_test):
        if self.model:
            predictions = self.model.predict(X_test)
            cm = confusion_matrix(y_test, predictions)
            report = classification_report(
                y_test, predictions, target_names=['Kisi1', 'Kisi2'], labels=[0, 1]
            )
            self.result_area.append(f"\nConfusion Matrix:\n{cm}\n\nClassification Report:\n{report}")
        else:
            self.result_area.append("Model henüz eğitilmedi.")

    def save_model(self):
        try:
            model_path = os.path.join(dataset_path, 'speaker_recognition_model.pkl')
            le_path = os.path.join(dataset_path, 'label_encoder.pkl')
            joblib.dump(self.model, model_path)
            joblib.dump(self.label_encoder, le_path)
            self.result_area.append(f"Model ve Etiket Kodlayıcı kaydedildi: {model_path}, {le_path}")
        except Exception as e:
            self.result_area.append(f"Model kaydetme hatası: {e}")

    def load_model(self):
        try:
            model_path = os.path.join(dataset_path, 'speaker_recognition_model.pkl')
            le_path = os.path.join(dataset_path, 'label_encoder.pkl')
            if os.path.exists(model_path) and os.path.exists(le_path):
                self.model = joblib.load(model_path)
                self.label_encoder = joblib.load(le_path)
                self.result_area.append(f"Model ve Etiket Kodlayıcı yüklendi: {model_path}, {le_path}")
            else:
                self.result_area.append("Model veya Etiket Kodlayıcı bulunamadı. Lütfen modeli eğitin.")
        except Exception as e:
            self.result_area.append(f"Model yükleme hatası: {e}")

    def record_and_predict(self):
        try:
            # Modelin yüklü olup olmadığını kontrol et
            if not self.model:
                self.load_model()
                if not self.model:
                    self.result_area.setText("Model yüklenemedi veya eğitilmedi.")
                    return

            # Kaydetme parametreleri
            fs = 16000  # Örnekleme hızı
            duration = 3  # Saniye
            self.result_area.append("Ses kaydediliyor...")

            # Ses kaydetme
            audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
            sd.wait()
            self.result_area.append("Ses kaydedildi.")

            # Ses verisini işleme
            audio_data = audio_data.flatten()
            audio_data = self.preprocess_audio(audio_data, fs)

            # Trim sonrası kontrol
            if len(audio_data) < fs * 2:
                self.result_area.append("Kaydedilen ses çok kısa. Lütfen daha uzun konuşun.")
                return

            features = self.extract_features(audio_data, fs)
            self.result_area.append(f"Çıkarılan Özellikler: {features}")

            # Tahmin yapma
            features = features.reshape(1, -1)  # Tahmin için şekillendirme
            prediction = self.model.predict(features)
            predicted_label = prediction[0]

            # Etiketi geri dönüştürme
            speaker = self.label_encoder.inverse_transform([predicted_label])[0]
            self.result_area.append(f"Tahmin edilen konuşmacı: {speaker}")

        except Exception as e:
            self.result_area.setText(f"Tahmin hatası: {str(e)}")

    def save_audio(self, audio_data, fs, filename):
        try:
            # Normalize audio data
            audio_data = librosa.util.normalize(audio_data)

            # Save as WAV file
            sf.write(filename, audio_data, fs)
            self.result_area.append(f"Ses dosyası kaydedildi: {filename}")
            return True
        except Exception as e:
            self.result_area.append(f"Ses kayıt hatası: {str(e)}")
            return False

    def predict_speaker_from_file(self, audio_file):
        try:
            # Load audio with same parameters as training
            audio, sr = librosa.load(audio_file, sr=16000, mono=True)

            # Extract features exactly like in training
            audio = self.preprocess_audio(audio, sr)
            features = self.extract_features(audio, sr)

            # Make prediction
            if self.model:
                features = features.reshape(1, -1)  # Reshape for prediction
                prediction = self.model.predict(features)
                speaker = self.label_encoder.inverse_transform(prediction)[0]
                return speaker
            else:
                return "Model not trained yet."

        except Exception as e:
            print(f"Prediction error: {e}")
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
