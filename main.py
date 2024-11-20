import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QStyleFactory
from tabs.emotion_tab import EmotionTab
from tabs.speech_tab import SpeechTab
from tabs.topic_tab import TopicTab
from utils.styles import COLORS
from tabs.histogram_tab import RecordingTab
from tabs.speaker_recognition_tab import SpeakerRecognitionTab
#from tabs.speech_tab import SpeechTab
#from tabs.emotion_tab import EmotionTab
#from tabs.topic_tab import TopicTab

class VoiceAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ses Analizi Uygulaması")
        self.setGeometry(100, 100, 1280, 720)
        self.setup_theme()

        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Başlık
        title = QLabel("Ses Analizi ve Duygu Tanıma Sistemi")
        title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['primary']};
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
            }}
        """)
        layout.addWidget(title, alignment=Qt.AlignCenter)

        # Tab widget oluşturma
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid #BDBDBD;
                border-radius: 5px;
                background: {COLORS['surface']};
            }}
            QTabBar::tab {{
                background: {COLORS['background']};
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background: {COLORS['primary']};
                color: white;
            }}
        """)
        layout.addWidget(tabs)

        # Tüm tabları ekleme
        tabs.addTab(RecordingTab(), "🎤 Ses Kaydı ve Histogram")
        tabs.addTab(SpeakerRecognitionTab(), "👤 Konuşmacı Tanıma")
        tabs.addTab(SpeechTab(), "💭 Konuşma Analizi")
        tabs.addTab(EmotionTab(), "😊 Duygu Analizi")
        tabs.addTab(TopicTab(), "📋 Konu Analizi")

    def setup_theme(self):
        # Genel tema ayarları
        self.setStyle(QStyleFactory.create('Fusion'))
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(COLORS['background']))
        palette.setColor(QPalette.WindowText, QColor(COLORS['text']))
        palette.setColor(QPalette.Base, QColor(COLORS['surface']))
        palette.setColor(QPalette.AlternateBase, QColor(COLORS['background']))
        palette.setColor(QPalette.ToolTipBase, QColor(COLORS['text']))
        palette.setColor(QPalette.ToolTipText, QColor(COLORS['surface']))
        palette.setColor(QPalette.Text, QColor(COLORS['text']))
        palette.setColor(QPalette.Button, QColor(COLORS['surface']))
        palette.setColor(QPalette.ButtonText, QColor(COLORS['text']))
        palette.setColor(QPalette.BrightText, QColor(COLORS['surface']))
        palette.setColor(QPalette.Highlight, QColor(COLORS['primary']))
        palette.setColor(QPalette.HighlightedText, QColor(COLORS['surface']))
        self.setPalette(palette)

        # Font ayarları
        app = QApplication.instance()
        font = QFont('Segoe UI', 10)
        app.setFont(font)

def main():
    app = QApplication(sys.argv)

    # Stil dosyası oluşturma
    style = """
        QMainWindow {
            background-color: #FAFAFA;
        }
        QLabel {
            color: #212121;
            font-size: 14px;
        }
        QLabel[title="true"] {
            font-size: 18px;
            font-weight: bold;
            color: #1976D2;
        }
    """
    app.setStyleSheet(style)

    window = VoiceAnalysisApp()
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()