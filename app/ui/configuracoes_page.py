from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
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
from app.services.backup_service import backup_service


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
            "Configure os dados do estabelecimento, "
            "relatórios e segurança dos dados."
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

        # ==================================================
        # Card do estabelecimento
        # ==================================================
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

        nome_label = QLabel(
            "Nome do estabelecimento"
        )

        self.nome_input = QLineEdit()

        self.nome_input.setPlaceholderText(
            "Exemplo: Mercadinho Central"
        )

        responsavel_label = QLabel(
            "Responsável"
        )

        self.responsavel_input = QLineEdit()

        self.responsavel_input.setPlaceholderText(
            "Exemplo: João da Silva"
        )

        email_label = QLabel(
            "E-mail para relatórios"
        )

        self.email_input = QLineEdit()

        self.email_input.setPlaceholderText(
            "Exemplo: gerente@empresa.com"
        )

        self.enviar_relatorio_check = QCheckBox(
            "Enviar relatório automaticamente "
            "ao fechar o caixa"
        )

        self.enviar_relatorio_check.setCursor(
            Qt.PointingHandCursor
        )

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

        # ==================================================
        # Card de backup e restauração
        # ==================================================
        backup_card = QFrame()

        backup_card.setObjectName(
            "historicoCard"
        )

        backup_layout = QVBoxLayout(
            backup_card
        )

        backup_layout.setContentsMargins(
            28,
            24,
            28,
            24,
        )

        backup_layout.setSpacing(
            14
        )

        backup_titulo = QLabel(
            "Backup e recuperação"
        )

        backup_titulo.setObjectName(
            "sectionTitle"
        )

        backup_descricao = QLabel(
            "O CaixaGo cria backups automáticos após "
            "o fechamento do caixa. Você também pode "
            "restaurar uma cópia anterior do banco de dados."
        )

        backup_descricao.setObjectName(
            "secondaryText"
        )

        backup_descricao.setWordWrap(
            True
        )

        aviso = QLabel(
            "A restauração substitui os dados atuais pelo "
            "conteúdo do backup selecionado. Antes disso, "
            "o CaixaGo cria uma cópia de segurança do estado atual."
        )

        aviso.setWordWrap(
            True
        )

        aviso.setStyleSheet(
            """
            color: #FBBF24;
            background-color: transparent;
            """
        )

        restaurar_button = QPushButton(
            "Restaurar backup"
        )

        restaurar_button.setObjectName(
            "ghostButton"
        )

        restaurar_button.clicked.connect(
            self.restaurar_backup
        )

        backup_layout.addWidget(
            backup_titulo
        )

        backup_layout.addWidget(
            backup_descricao
        )

        backup_layout.addWidget(
            aviso
        )

        backup_layout.addSpacing(
            6
        )

        backup_layout.addWidget(
            restaurar_button
        )

        root.addWidget(
            backup_card
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

    def restaurar_backup(self) -> None:
        caixa = caixa_controller.obter_caixa_aberto()

        if caixa is not None:
            QMessageBox.warning(
                self,
                "Restauração bloqueada",
                (
                    "Não é possível restaurar um backup "
                    "enquanto existe um caixa aberto.\n\n"
                    "Feche o caixa atual antes de continuar."
                ),
            )
            return

        caminho, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar backup do CaixaGo",
            str(
                backup_service.backup_directory
            ),
            "Banco de dados (*.db)",
        )

        if not caminho:
            return

        primeira_confirmacao = QMessageBox.warning(
            self,
            "Confirmar restauração",
            (
                "A restauração substituirá os dados atuais "
                "pelos dados do backup selecionado.\n\n"
                "Antes da substituição, o CaixaGo criará "
                "automaticamente um backup do estado atual.\n\n"
                "Deseja continuar?"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if primeira_confirmacao != QMessageBox.Yes:
            return

        segunda_confirmacao = QMessageBox.question(
            self,
            "Confirmação final",
            (
                "Esta é a última confirmação.\n\n"
                "Após restaurar o banco de dados, "
                "o CaixaGo será encerrado e deverá "
                "ser aberto novamente.\n\n"
                "Restaurar agora?"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if segunda_confirmacao != QMessageBox.Yes:
            return

        try:
            backup_service.restaurar_backup(
                caminho
            )

            QMessageBox.information(
                self,
                "Backup restaurado",
                (
                    "Backup restaurado com sucesso.\n\n"
                    "O CaixaGo será encerrado agora.\n"
                    "Abra o programa novamente para "
                    "carregar os dados restaurados."
                ),
            )

            QApplication.quit()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Falha na restauração",
                (
                    "Não foi possível restaurar "
                    "o backup.\n\n"
                    f"{error}"
                ),
            )

    def voltar(self) -> None:
        if self.on_voltar is not None:
            self.on_voltar()