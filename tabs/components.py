from PyQt5.QtWidgets import QPushButton, QProgressBar
from utils.styles import COLORS, adjust_color

class StyledButton(QPushButton):
    def __init__(self, text, color=COLORS['primary']):
        super().__init__(text)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: black;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {adjust_color(color, 1.1)};
            }}
            QPushButton:pressed {{
                background-color: {adjust_color(color, 0.9)};
            }}
            QPushButton:disabled {{
                background-color: #BDBDBD;
            }}
        """)

class StyledProgressBar(QProgressBar):
    def __init__(self, color):
        super().__init__()
        self.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 5px;
                text-align: center;
                background-color: #E0E0E0;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)
        self.setTextVisible(True)