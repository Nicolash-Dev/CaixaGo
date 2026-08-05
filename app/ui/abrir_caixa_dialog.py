from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDoubleSpinBox,
    QLineEdit,
    QPushButton,
    QMessageBox,
)

from app.controllers.caixa_controller import caixa_controller


class AbrirCaixaDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Abrir Caixa")
        self.setModal(True)
        self.setFixedWidth(440)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        title = QLabel("Abrir Caixa")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Informe o valor inicial disponível para troco."
        )
        subtitle.setObjectName("secondaryText")
        subtitle.setWordWrap(True)

        valor_label = QLabel("Valor inicial")

        self.valor_input = QDoubleSpinBox()
        self.valor_input.setRange(0, 999999999)
        self.valor_input.setDecimals(2)
        self.valor_input.setPrefix("R$ ")
        self.valor_input.setSingleStep(10)
        self.valor_input.setMinimumHeight(48)

        observacao_label = QLabel("Observação opcional")

        self.observacao_input = QLineEdit()
        self.observacao_input.setPlaceholderText(
            "Exemplo: Troco inicial"
        )

        buttons = QHBoxLayout()

        cancelar_button = QPushButton("Cancelar")
        cancelar_button.setObjectName("ghostButton")
        cancelar_button.clicked.connect(self.reject)

        abrir_button = QPushButton("Abrir Caixa")
        abrir_button.setObjectName("primaryButton")
        abrir_button.clicked.connect(self.salvar)

        buttons.addWidget(cancelar_button)
        buttons.addWidget(abrir_button)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)
        layout.addWidget(valor_label)
        layout.addWidget(self.valor_input)
        layout.addWidget(observacao_label)
        layout.addWidget(self.observacao_input)
        layout.addSpacing(10)
        layout.addLayout(buttons)

    def salvar(self) -> None:
        try:
            caixa_controller.abrir_caixa(
                valor_inicial=self.valor_input.value(),
                observacao=self.observacao_input.text(),
            )

            self.accept()

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Não foi possível abrir o caixa",
                str(error),
            )

        except Exception:
            QMessageBox.critical(
                self,
                "Não foi possível abrir o caixa",
                "Ocorreu um problema inesperado.",
            )