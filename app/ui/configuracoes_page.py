from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.controllers.caixa_controller import caixa_controller


class ConfiguracoesPage(QWidget):
    def __init__(
        self,
        on_voltar=None,
    ) -> None:
        super().__init__()

        self.on_voltar = on_voltar

        self.criar_interface()

    def criar_interface(self) -> None:
        root = QVBoxLayout(self)

        root.setContentsMargins(
            42,
            32,
            42,
            32,
        )

        root.setSpacing(20)

        # Cabeçalho
        header = QHBoxLayout()

        titulo_container = QVBoxLayout()

        titulo = QLabel(
            "Configurações"
        )
        titulo.setObjectName(
            "pageTitle"
        )

        subtitulo = QLabel(
            "Configure os dados do estabelecimento "
            "e o envio dos relatórios."
        )
        subtitulo.setObjectName(
            "secondaryText"
        )

        titulo_container.addWidget(
            titulo
        )

        titulo_container.addWidget(
            subtitulo
        )

        voltar_button = QPushButton(
            "Voltar"
        )

        voltar_button.setObjectName(
            "ghostButton"
        )

        voltar_button.setFixedWidth(
            120
        )

        voltar_button.clicked.connect(
            self.voltar
        )

        header.addLayout(
            titulo_container
        )

        header.addStretch()

        header.addWidget(
            voltar_button
        )

        root.addLayout(
            header
        )

        # Card principal
        card = QFrame()

        card.setObjectName(
            "historicoCard"
        )

        card_layout = QVBoxLayout(
            card
        )

        card_layout.setContentsMargins(
            28,
            24,
            28,
            24,
        )

        card_layout.setSpacing(
            16
        )

        titulo_estabelecimento = QLabel(
            "Estabelecimento"
        )

        titulo_estabelecimento.setObjectName(
            "sectionTitle"
        )

        descricao = QLabel(
            "Essas informações serão utilizadas "
            "nos relatórios e futuras automações."
        )

        descricao.setObjectName(
            "secondaryText"
        )

        descricao.setWordWrap(
            True
        )

        # Nome
        nome_label = QLabel(
            "Nome do estabelecimento"
        )

        self.nome_input = QLineEdit()

        self.nome_input.setPlaceholderText(
            "Exemplo: Mercadinho Central"
        )

        # Responsável
        responsavel_label = QLabel(
            "Responsável"
        )

        self.responsavel_input = QLineEdit()

        self.responsavel_input.setPlaceholderText(
            "Exemplo: João da Silva"
        )

        # Email
        email_label = QLabel(
            "E-mail para relatórios"
        )

        self.email_input = QLineEdit()

        self.email_input.setPlaceholderText(
            "Exemplo: gerente@empresa.com"
        )

        # Envio automático
        self.enviar_relatorio_check = QCheckBox(
            "Enviar relatório automaticamente "
            "ao fechar o caixa"
        )

        self.enviar_relatorio_check.setCursor(
            Qt.PointingHandCursor
        )

        # Botão salvar
        salvar_button = QPushButton(
            "Salvar configurações"
        )

        salvar_button.setObjectName(
            "primaryButton"
        )

        salvar_button.clicked.connect(
            self.salvar
        )

        card_layout.addWidget(
            titulo_estabelecimento
        )

        card_layout.addWidget(
            descricao
        )

        card_layout.addSpacing(
            8
        )

        card_layout.addWidget(
            nome_label
        )

        card_layout.addWidget(
            self.nome_input
        )

        card_layout.addWidget(
            responsavel_label
        )

        card_layout.addWidget(
            self.responsavel_input
        )

        card_layout.addWidget(
            email_label
        )

        card_layout.addWidget(
            self.email_input
        )

        card_layout.addSpacing(
            8
        )

        card_layout.addWidget(
            self.enviar_relatorio_check
        )

        card_layout.addSpacing(
            12
        )

        card_layout.addWidget(
            salvar_button
        )

        root.addWidget(
            card
        )

        root.addStretch()

    def carregar_configuracoes(
        self,
    ) -> None:
        try:
            configuracoes = (
                caixa_controller
                .obter_configuracoes_estabelecimento()
            )

            self.nome_input.setText(
                configuracoes.get(
                    "nome",
                    ""
                )
            )

            self.responsavel_input.setText(
                configuracoes.get(
                    "responsavel",
                    ""
                )
            )

            self.email_input.setText(
                configuracoes.get(
                    "email_relatorios",
                    ""
                )
            )

            self.enviar_relatorio_check.setChecked(
                bool(
                    configuracoes.get(
                        "enviar_relatorio",
                        False
                    )
                )
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro",
                (
                    "Não foi possível carregar "
                    "as configurações.\n\n"
                    f"{error}"
                ),
            )

    def salvar(self) -> None:
        try:
            caixa_controller.salvar_configuracoes_estabelecimento(
                nome=self.nome_input.text(),
                responsavel=self.responsavel_input.text(),
                email_relatorios=self.email_input.text(),
                enviar_relatorio=(
                    self.enviar_relatorio_check
                    .isChecked()
                ),
            )

            QMessageBox.information(
                self,
                "Configurações",
                "Configurações salvas com sucesso.",
            )

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Não foi possível salvar",
                str(error),
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro",
                (
                    "Ocorreu um problema inesperado.\n\n"
                    f"{error}"
                ),
            )

    def voltar(self) -> None:
        if self.on_voltar is not None:
            self.on_voltar()