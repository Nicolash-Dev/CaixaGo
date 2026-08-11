from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.controllers.caixa_controller import caixa_controller


class MovimentacaoDialog(QDialog):
    def __init__(
        self,
        parent=None,
        tipo_inicial: str = "VENDA",
    ) -> None:
        super().__init__(parent)

        self.setWindowTitle("Novo Evento")
        self.setModal(True)
        self.setFixedWidth(440)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        title = QLabel("Novo Evento")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Registre uma movimentação no caixa aberto."
        )
        subtitle.setObjectName("secondaryText")
        subtitle.setWordWrap(True)

        tipo_label = QLabel("Tipo de evento")

        self.tipo_input = QComboBox()
        self.tipo_input.addItem("Venda", "VENDA")
        self.tipo_input.addItem("Sangria", "SANGRIA")
        self.tipo_input.addItem("Suprimento", "SUPRIMENTO")

        self.tipo_input.currentIndexChanged.connect(
            self.atualizar_campos
        )

        indice = self.tipo_input.findData(
            tipo_inicial
        )

        if indice >= 0:
            self.tipo_input.setCurrentIndex(
                indice
            )

        valor_label = QLabel("Valor")

        self.valor_input = QDoubleSpinBox()
        self.valor_input.setRange(
            0.01,
            999999999.99,
        )
        self.valor_input.setDecimals(2)
        self.valor_input.setPrefix("R$ ")
        self.valor_input.setSingleStep(10.00)
        self.valor_input.setMinimumHeight(48)

        # Forma de pagamento
        self.forma_pagamento_label = QLabel(
            "Forma de pagamento"
        )

        self.forma_pagamento_input = QComboBox()

        self.forma_pagamento_input.addItem(
            "Dinheiro",
            "DINHEIRO",
        )

        self.forma_pagamento_input.addItem(
            "PIX",
            "PIX",
        )

        self.forma_pagamento_input.addItem(
            "Débito",
            "DEBITO",
        )

        self.forma_pagamento_input.addItem(
            "Crédito",
            "CREDITO",
        )

        descricao_label = QLabel(
            "Descrição opcional"
        )

        self.descricao_input = QLineEdit()
        self.descricao_input.setPlaceholderText(
            "Exemplo: Venda do balcão"
        )

        buttons = QHBoxLayout()

        cancelar_button = QPushButton(
            "Cancelar"
        )
        cancelar_button.setObjectName(
            "ghostButton"
        )
        cancelar_button.clicked.connect(
            self.reject
        )

        salvar_button = QPushButton(
            "Salvar Evento"
        )
        salvar_button.setObjectName(
            "primaryButton"
        )
        salvar_button.clicked.connect(
            self.salvar
        )

        buttons.addWidget(
            cancelar_button
        )
        buttons.addWidget(
            salvar_button
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)

        layout.addWidget(
            tipo_label
        )
        layout.addWidget(
            self.tipo_input
        )

        layout.addWidget(
            valor_label
        )
        layout.addWidget(
            self.valor_input
        )

        layout.addWidget(
            self.forma_pagamento_label
        )
        layout.addWidget(
            self.forma_pagamento_input
        )

        layout.addWidget(
            descricao_label
        )
        layout.addWidget(
            self.descricao_input
        )

        layout.addSpacing(10)
        layout.addLayout(buttons)

        # Atualiza a tela conforme o tipo inicial
        self.atualizar_campos()

    def atualizar_campos(self) -> None:
        tipo = self.tipo_input.currentData()

        eh_venda = tipo == "VENDA"

        self.forma_pagamento_label.setVisible(
            eh_venda
        )

        self.forma_pagamento_input.setVisible(
            eh_venda
        )

        if tipo == "VENDA":
            self.descricao_input.setPlaceholderText(
                "Exemplo: Venda do balcão"
            )

        elif tipo == "SANGRIA":
            self.descricao_input.setPlaceholderText(
                "Exemplo: Retirada para pagamento"
            )

        elif tipo == "SUPRIMENTO":
            self.descricao_input.setPlaceholderText(
                "Exemplo: Reforço de troco"
            )

    def salvar(self) -> None:
        try:
            tipo = self.tipo_input.currentData()

            forma_pagamento = None

            if tipo == "VENDA":
                forma_pagamento = (
                    self.forma_pagamento_input
                    .currentData()
                )

            caixa_controller.registrar_movimentacao(
                tipo=tipo,
                valor=self.valor_input.value(),
                descricao=self.descricao_input.text(),
                forma_pagamento=forma_pagamento,
            )

            self.accept()

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Não foi possível registrar",
                str(error),
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Não foi possível registrar",
                (
                    "Ocorreu um problema inesperado.\n\n"
                    f"{error}"
                ),
            )