from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class SplashScreen(QWidget):
    def __init__(self, on_finished) -> None:
        super().__init__()
        self.on_finished = on_finished

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(620, 360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(42, 42, 42, 42)

        card = QWidget()
        card.setObjectName("splashCard")
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(14)

        logo = QLabel("C✓")
        logo.setObjectName("splashLogo")
        logo.setAlignment(Qt.AlignCenter)

        title = QLabel("CaixaGo")
        title.setObjectName("splashTitle")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 28, QFont.Bold))

        slogan = QLabel("Conte o dinheiro. O resto é com a gente.")
        slogan.setObjectName("splashSlogan")
        slogan.setAlignment(Qt.AlignCenter)

        status = QLabel("Preparando seu caixa...")
        status.setObjectName("splashStatus")
        status.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(logo)
        card_layout.addWidget(title)
        card_layout.addWidget(slogan)
        card_layout.addSpacing(18)
        card_layout.addWidget(status)

        layout.addWidget(card)

        QTimer.singleShot(2200, self.finish)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        screen = self.screen().availableGeometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2,
        )

    def finish(self) -> None:
        self.close()
        self.on_finished()
