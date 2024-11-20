from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
import numpy as np

class SpeakerRecognitionTab(QWidget):
    def __init__(self):
        super().__init__()
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

        self.setLayout(layout)

    def train_model(self):
        # Örnek veri seti
        X = np.random.rand(100, 10)  # 100 örnek, 10 özellik
        y = np.random.randint(0, 2, 100)  # İkili sınıflandırma (0 veya 1)

        # Veri setini ayırma
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Model oluşturma ve eğitme
        model = RandomForestClassifier()
        model.fit(X_train, y_train)

        # Tahmin ve metrik hesaplama
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        fm = f1_score(y_test, y_pred)

        # Sonuçları gösterme
        self.result_area.setText(f"Accuracy (Doğruluk): {acc:.2f}\nF-Score (FM): {fm:.2f}")
