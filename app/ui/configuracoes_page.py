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
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.controllers.caixa_controller import caixa_controller
from app.services.backup_service import backup_service
from app.services.credential_service import credential_service
from app.services.email_service import email_service


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
        root.setContentsMargins(34, 24, 34, 24)
        root.setSpacing(14)

        # Cabeçalho fixo
        header = QHBoxLayout()
        header.setSpacing(16)

        titulo_container = QVBoxLayout()
        titulo_container.setSpacing(4)

        titulo = QLabel("Configurações")
        titulo.setObjectName("pageTitle")

        subtitulo = QLabel(
            "Configure os dados do estabelecimento, "
            "relatórios e segurança dos dados."
        )
        subtitulo.setObjectName("secondaryText")

        titulo_container.addWidget(titulo)
        titulo_container.addWidget(subtitulo)

        voltar_button = QPushButton("Voltar")
        voltar_button.setObjectName("ghostButton")
        voltar_button.setFixedWidth(120)
        voltar_button.clicked.connect(self.voltar)

        header.addLayout(titulo_container)
        header.addStretch()
        header.addWidget(voltar_button)

        root.addLayout(header)

        # Área rolável
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        content.setObjectName("configScrollContent")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 4, 10, 8)
        content_layout.setSpacing(14)

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

        card_layout.setContentsMargins(24, 18, 24, 18)

        card_layout.setSpacing(11)

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

        content_layout.addWidget(card)

        # ==================================================
        # Card de e-mail seguro
        # ==================================================
        email_card = QFrame()
        email_card.setObjectName("historicoCard")

        email_layout = QVBoxLayout(email_card)
        email_layout.setContentsMargins(24, 18, 24, 18)
        email_layout.setSpacing(10)

        email_titulo = QLabel("E-mail do CaixaGo")
        email_titulo.setObjectName("sectionTitle")

        email_descricao = QLabel(
            "Configure a conta usada para enviar relatórios. "
            "A senha é armazenada pelo gerenciador de credenciais "
            "do sistema e não é gravada no banco de dados."
        )
        email_descricao.setObjectName("secondaryText")
        email_descricao.setWordWrap(True)

        smtp_usuario_label = QLabel("Usuário SMTP")
        self.smtp_usuario_input = QLineEdit()
        self.smtp_usuario_input.setPlaceholderText(
            "Exemplo: caixago.empresa@gmail.com"
        )

        smtp_senha_label = QLabel("Senha de app")
        self.smtp_senha_input = QLineEdit()
        self.smtp_senha_input.setEchoMode(QLineEdit.Password)
        self.smtp_senha_input.setPlaceholderText(
            "Digite para salvar ou substituir a credencial"
        )

        self.smtp_status_label = QLabel(
            "Nenhuma credencial segura carregada."
        )
        self.smtp_status_label.setObjectName("secondaryText")

        email_botoes = QHBoxLayout()

        salvar_credencial_button = QPushButton(
            "Salvar credencial"
        )
        salvar_credencial_button.setObjectName("primaryButton")
        salvar_credencial_button.clicked.connect(
            self.salvar_credencial_email
        )

        testar_email_button = QPushButton(
            "Enviar e-mail de teste"
        )
        testar_email_button.setObjectName("ghostButton")
        testar_email_button.clicked.connect(
            self.enviar_email_teste
        )

        email_botoes.addWidget(salvar_credencial_button)
        email_botoes.addWidget(testar_email_button)

        email_layout.addWidget(email_titulo)
        email_layout.addWidget(email_descricao)
        email_layout.addSpacing(6)
        email_layout.addWidget(smtp_usuario_label)
        email_layout.addWidget(self.smtp_usuario_input)
        email_layout.addWidget(smtp_senha_label)
        email_layout.addWidget(self.smtp_senha_input)
        email_layout.addWidget(self.smtp_status_label)
        email_layout.addSpacing(6)
        email_layout.addLayout(email_botoes)

        content_layout.addWidget(email_card)

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

        backup_layout.setContentsMargins(24, 18, 24, 18)

        backup_layout.setSpacing(10)

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

        content_layout.addWidget(backup_card)

        content_layout.addStretch()

        scroll.setWidget(content)
        root.addWidget(scroll)
        self.scroll_area = scroll

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

            resumo_email = email_service.obter_resumo_configuracao()
            usuario_smtp = resumo_email.get("usuario", "")
            self.smtp_usuario_input.setText(usuario_smtp)

            senha_segura = (
                credential_service.obter_senha_smtp(usuario_smtp)
                if usuario_smtp
                else None
            )

            if senha_segura:
                email_service.configurar(
                    usuario=usuario_smtp,
                    senha=senha_segura,
                    remetente=(
                        resumo_email.get("remetente", "")
                        or usuario_smtp
                    ),
                    host=resumo_email.get(
                        "host",
                        "smtp.gmail.com",
                    ),
                    porta=int(resumo_email.get("porta", 587)),
                    usar_tls=bool(
                        resumo_email.get("usar_tls", True)
                    ),
                )
                self.smtp_status_label.setText(
                    "Credencial segura carregada."
                )
            else:
                self.smtp_status_label.setText(
                    "Informe o usuário e a senha de app."
                )

            self.smtp_senha_input.clear()

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

    def salvar_credencial_email(self) -> None:
        try:
            usuario = self.smtp_usuario_input.text().strip()
            senha = self.smtp_senha_input.text().strip()

            if not usuario:
                raise ValueError("Informe o usuário SMTP.")

            if not senha:
                raise ValueError("Informe a senha de app.")

            credential_service.salvar_senha_smtp(
                usuario=usuario,
                senha=senha,
            )

            email_service.configurar(
                usuario=usuario,
                senha=senha,
                remetente=usuario,
            )

            self.smtp_senha_input.clear()
            self.smtp_status_label.setText(
                "Credencial salva com segurança."
            )

            QMessageBox.information(
                self,
                "E-mail",
                "Credencial de e-mail salva com sucesso.",
            )

        except Exception as error:
            QMessageBox.warning(
                self,
                "Não foi possível salvar",
                str(error),
            )

    def enviar_email_teste(self) -> None:
        try:
            usuario = self.smtp_usuario_input.text().strip()

            if not usuario:
                raise ValueError("Informe o usuário SMTP.")

            senha = credential_service.obter_senha_smtp(
                usuario
            )

            if not senha:
                raise ValueError(
                    "Salve a credencial antes de testar."
                )

            email_service.configurar(
                usuario=usuario,
                senha=senha,
                remetente=usuario,
            )

            destinatario = self.email_input.text().strip()

            if not destinatario:
                raise ValueError(
                    "Informe o e-mail para relatórios "
                    "na seção Estabelecimento."
                )

            estabelecimento = (
                self.nome_input.text().strip()
                or "CaixaGo"
            )

            email_service.enviar_email_teste(
                destinatario=destinatario,
                estabelecimento=estabelecimento,
            )

            QMessageBox.information(
                self,
                "E-mail",
                (
                    "E-mail de teste enviado com sucesso "
                    f"para {destinatario}."
                ),
            )

        except Exception as error:
            QMessageBox.warning(
                self,
                "Falha no teste de e-mail",
                str(error),
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