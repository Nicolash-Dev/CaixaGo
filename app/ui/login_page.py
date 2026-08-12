from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.controllers.caixa_controller import caixa_controller


class LoginPage(QWidget):
    def __init__(
        self,
        on_login_success,
    ) -> None:
        super().__init__()

        self.on_login_success = on_login_success

        root = QHBoxLayout(self)
        root.setContentsMargins(
            90,
            70,
            90,
            70,
        )
        root.setAlignment(
            Qt.AlignCenter
        )

        card = QFrame()
        card.setObjectName(
            "loginCard"
        )
        card.setMaximumWidth(
            460
        )

        layout = QVBoxLayout(
            card
        )
        layout.setContentsMargins(
            42,
            42,
            42,
            42,
        )
        layout.setSpacing(
            18
        )

        logo = QLabel("C✓")
        logo.setObjectName(
            "brandMark"
        )
        logo.setAlignment(
            Qt.AlignCenter
        )

        title = QLabel(
            "CaixaGo"
        )
        title.setObjectName(
            "pageTitle"
        )
        title.setAlignment(
            Qt.AlignCenter
        )

        subtitle = QLabel(
            "Entre com seu usuário e PIN"
        )
        subtitle.setObjectName(
            "secondaryText"
        )
        subtitle.setAlignment(
            Qt.AlignCenter
        )

        usuario_label = QLabel(
            "Usuário"
        )

        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText(
            "Digite seu usuário"
        )
        self.usuario_input.setMaxLength(
            50
        )

        pin_label = QLabel(
            "PIN"
        )

        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText(
            "••••"
        )
        self.pin_input.setEchoMode(
            QLineEdit.Password
        )
        self.pin_input.setMaxLength(
            4
        )
        self.pin_input.setAlignment(
            Qt.AlignCenter
        )

        self.pin_input.returnPressed.connect(
            self.validate_login
        )

        self.message = QLabel("")
        self.message.setObjectName(
            "errorText"
        )
        self.message.setAlignment(
            Qt.AlignCenter
        )
        self.message.setWordWrap(
            True
        )

        enter_button = QPushButton(
            "Entrar"
        )
        enter_button.setObjectName(
            "primaryButton"
        )
        enter_button.clicked.connect(
            self.validate_login
        )

        layout.addWidget(
            logo
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            subtitle
        )

        layout.addSpacing(
            8
        )

        layout.addWidget(
            usuario_label
        )

        layout.addWidget(
            self.usuario_input
        )

        layout.addWidget(
            pin_label
        )

        layout.addWidget(
            self.pin_input
        )

        layout.addWidget(
            self.message
        )

        layout.addWidget(
            enter_button
        )

        root.addWidget(
            card
        )

        self.usuario_input.setFocus()

    def validate_login(
        self,
    ) -> None:
        usuario = (
            self.usuario_input
            .text()
            .strip()
        )

        pin = (
            self.pin_input
            .text()
            .strip()
        )

        if not usuario:
            self.message.setText(
                "Informe o usuário."
            )

            self.usuario_input.setFocus()
            return

        if not pin:
            self.message.setText(
                "Informe o PIN."
            )

            self.pin_input.setFocus()
            return

        try:
            usuario_logado = (
                caixa_controller
                .autenticar_usuario(
                    usuario=usuario,
                    pin=pin,
                )
            )

            self.message.setText("")

            self.pin_input.clear()

            self.on_login_success()

        except ValueError as error:
            self.message.setText(
                str(error)
            )

            self.pin_input.clear()
            self.pin_input.setFocus()

        except Exception:
            self.message.setText(
                "Ocorreu um problema ao realizar o login."
            )

            self.pin_input.clear()
            self.pin_input.setFocus()

    def reset_pin(
        self,
    ) -> None:
        self.pin_input.clear()
        self.message.setText("")
        self.usuario_input.setFocus()