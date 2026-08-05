from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame
)

from app.config import DEFAULT_USER_NAME, DEFAULT_USER_PIN


class LoginPage(QWidget):
    def __init__(self, on_login_success) -> None:
        super().__init__()
        self.on_login_success = on_login_success

        root = QHBoxLayout(self)
        root.setContentsMargins(90, 70, 90, 70)
        root.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setMaximumWidth(460)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(42, 42, 42, 42)
        layout.setSpacing(18)

        logo = QLabel("C✓")
        logo.setObjectName("brandMark")
        logo.setAlignment(Qt.AlignCenter)

        title = QLabel(f"Olá, {DEFAULT_USER_NAME}")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Digite seu PIN para continuar")
        subtitle.setObjectName("secondaryText")
        subtitle.setAlignment(Qt.AlignCenter)

        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText("••••")
        self.pin_input.setEchoMode(QLineEdit.Password)
        self.pin_input.setMaxLength(4)
        self.pin_input.setAlignment(Qt.AlignCenter)
        self.pin_input.returnPressed.connect(self.validate_pin)

        self.message = QLabel("")
        self.message.setObjectName("errorText")
        self.message.setAlignment(Qt.AlignCenter)

        enter_button = QPushButton("Entrar")
        enter_button.setObjectName("primaryButton")
        enter_button.clicked.connect(self.validate_pin)

        change_user = QPushButton("Trocar usuário")
        change_user.setObjectName("ghostButton")
        change_user.setEnabled(False)
        change_user.setToolTip("Disponível em uma versão futura")

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)
        layout.addWidget(self.pin_input)
        layout.addWidget(self.message)
        layout.addWidget(enter_button)
        layout.addWidget(change_user)

        root.addWidget(card)

    def validate_pin(self) -> None:
        if self.pin_input.text() == DEFAULT_USER_PIN:
            self.message.setText("")
            self.on_login_success()
        else:
            self.message.setText("PIN incorreto. Tente novamente.")
            self.pin_input.clear()
            self.pin_input.setFocus()

    def reset_pin(self) -> None:
        self.pin_input.clear()
        self.message.setText("")
        self.pin_input.setFocus()
