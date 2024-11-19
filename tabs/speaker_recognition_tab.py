import os
import librosa
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
)

class SpeakerRecognitionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.model = None
        self.dataset = pd.DataFrame()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Başlık
        self.title = QLabel("Konuşmacı Tanıma")
        self.title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1976D2;")
        layout.addWidget(self.title)

        # Ses dosyası ekleme düğmesi
        self.add_data_button = QPushButton("Ses Dosyalarını Ekle")
        self.add_data_button.clicked.connect(self.add_files)
        layout.addWidget(self.add_data_button)

        # Model eğitme düğmesi
        self.train_model_button = QPushButton("Modeli Eğit")
        self.train_model_button.clicked.connect(self.train_model)
        layout.addWidget(self.train_model_button)

        # Model test etme düğmesi
        self.test_model_button = QPushButton("Modeli Test Et")
        self.test_model_button.clicked.connect(self.test_model)
        layout.addWidget(self.test_model_button)

        # Sonuç etiketi
        self.result_label = QLabel("Sonuçlar burada gösterilecek.")
        self.result_label.setStyleSheet("font-size: 14px; color: #424242;")
        layout.addWidget(self.result_label)

    def extract_features(self, file_name):
        """
        Ses dosyasından MFCC özelliklerini çıkarır.
        """
        try:
            audio, sample_rate = librosa.load(file_name, res_type='kaiser_fast')
            mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
            return np.mean(mfccs.T, axis=0)
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Ses özellikleri çıkarılamadı: {str(e)}")
            return None

    def add_files(self):
        """
        Kullanıcıdan ses dosyalarını seçmesini ister ve veri setine ekler.
        """
        files, _ = QFileDialog.getOpenFileNames(self, "Ses Dosyalarını Seç", "", "Ses Dosyaları (*.wav *.mp3)")
        if not files:
            return

        data = []
        labels = []

        for file in files:
            label = os.path.basename(file).split("_")[0]  # Örnek: "Kişi1_ses1.wav"
            features = self.extract_features(file)
            if features is not None:
                data.append(features)
                labels.append(label)

        new_data = pd.DataFrame(data)
        new_data['label'] = labels

        # Veri setini güncelle
        self.dataset = pd.concat([self.dataset, new_data], ignore_index=True)
        QMessageBox.information(self, "Başarılı", f"{len(files)} ses dosyası eklendi.")

    def train_model(self):
        """
        Veri seti kullanarak modeli eğitir.
        """
        if self.dataset.empty:
            QMessageBox.warning(self, "Hata", "Eğitim için yeterli veri bulunmuyor.")
            return

        X = self.dataset.iloc[:, :-1].values
        y = self.dataset['label']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model = RandomForestClassifier()
        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')

        self.result_label.setText(f"Model Eğitildi.\nDoğruluk (ACC): {acc:.2f}\nF1 Skoru: {f1:.2f}")
        QMessageBox.information(self, "Başarılı", "Model başarıyla eğitildi.")

    def test_model(self):
        """
        Kullanıcıdan bir test dosyası alır ve model tahminini yapar.
        """
        if self.model is None:
            QMessageBox.warning(self, "Hata", "Model henüz eğitilmedi.")
            return

        test_file, _ = QFileDialog.getOpenFileName(self, "Test için Ses Dosyasını Seç", "", "Ses Dosyaları (*.wav *.mp3)")
        if not test_file:
            return

        features = self.extract_features(test_file)
        if features is None:
            return

        prediction = self.model.predict([features])[0]
        self.result_label.setText(f"Tahmin Edilen Kişi: {prediction}")
        QMessageBox.information(self, "Sonuç", f"Ses dosyası tanımlandı: {prediction}")
