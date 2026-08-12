from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
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


class UsuarioDialog(QDialog):
    def __init__(
        self,
        parent=None,
        usuario=None,
    ) -> None:
        super().__init__(parent)

        self.usuario = usuario

        self.setModal(True)
        self.setMinimumWidth(420)

        if usuario is None:
            self.setWindowTitle("Novo usuário")
        else:
            self.setWindowTitle("Editar usuário")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            28,
            28,
            28,
            28,
        )
        layout.setSpacing(18)

        titulo = QLabel(
            "Novo usuário"
            if usuario is None
            else "Editar usuário"
        )
        titulo.setObjectName(
            "pageTitle"
        )

        form = QFormLayout()
        form.setSpacing(14)

        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText(
            "Nome completo"
        )

        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText(
            "Login"
        )

        self.perfil_input = QComboBox()
        self.perfil_input.addItem(
            "Operador",
            "OPERADOR",
        )
        self.perfil_input.addItem(
            "Gerente",
            "GERENTE",
        )

        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText(
            "4 números"
        )
        self.pin_input.setEchoMode(
            QLineEdit.Password
        )
        self.pin_input.setMaxLength(
            4
        )

        form.addRow(
            "Nome",
            self.nome_input,
        )

        form.addRow(
            "Usuário",
            self.usuario_input,
        )

        form.addRow(
            "Perfil",
            self.perfil_input,
        )

        form.addRow(
            "PIN",
            self.pin_input,
        )

        if usuario is not None:
            self.nome_input.setText(
                str(usuario["nome"])
            )

            self.usuario_input.setText(
                str(usuario["usuario"])
            )

            indice = (
                self.perfil_input
                .findData(
                    str(usuario["perfil"]).upper()
                )
            )

            if indice >= 0:
                self.perfil_input.setCurrentIndex(
                    indice
                )

            self.pin_input.setPlaceholderText(
                "Deixe vazio para manter o PIN"
            )

        botoes = QHBoxLayout()

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
            "Salvar"
        )
        salvar_button.setObjectName(
            "primaryButton"
        )
        salvar_button.clicked.connect(
            self.salvar
        )

        botoes.addWidget(
            cancelar_button
        )

        botoes.addWidget(
            salvar_button
        )

        layout.addWidget(
            titulo
        )

        layout.addLayout(
            form
        )

        layout.addLayout(
            botoes
        )

    def salvar(self) -> None:
        nome = (
            self.nome_input
            .text()
            .strip()
        )

        usuario_login = (
            self.usuario_input
            .text()
            .strip()
        )

        perfil = (
            self.perfil_input
            .currentData()
        )

        pin = (
            self.pin_input
            .text()
            .strip()
        )

        try:
            if self.usuario is None:
                caixa_controller.criar_usuario(
                    nome=nome,
                    usuario=usuario_login,
                    pin=pin,
                    perfil=perfil,
                )

            else:
                usuario_id = int(
                    self.usuario["id"]
                )

                caixa_controller.atualizar_usuario(
                    usuario_id=usuario_id,
                    nome=nome,
                    usuario=usuario_login,
                    perfil=perfil,
                )

                if pin:
                    caixa_controller.atualizar_pin_usuario(
                        usuario_id=usuario_id,
                        novo_pin=pin,
                    )

            self.accept()

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


class UsuariosPage(QWidget):
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

        root.setSpacing(
            20
        )

        header = QHBoxLayout()

        titulo_container = QVBoxLayout()

        titulo = QLabel(
            "Usuários"
        )
        titulo.setObjectName(
            "pageTitle"
        )

        subtitulo = QLabel(
            "Gerencie operadores e gerentes do CaixaGo."
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

        novo_button = QPushButton(
            "Novo usuário"
        )
        novo_button.setObjectName(
            "primaryButton"
        )
        novo_button.clicked.connect(
            self.novo_usuario
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
            novo_button
        )

        header.addWidget(
            voltar_button
        )

        root.addLayout(
            header
        )

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(
            True
        )
        self.scroll.setFrameShape(
            QFrame.NoFrame
        )
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.container = QWidget()

        self.lista = QVBoxLayout(
            self.container
        )

        self.lista.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.lista.setSpacing(
            14
        )

        self.lista.setAlignment(
            Qt.AlignTop
        )

        self.scroll.setWidget(
            self.container
        )

        root.addWidget(
            self.scroll
        )

    def carregar_usuarios(
        self,
    ) -> None:
        self.limpar_lista()

        try:
            usuarios = (
                caixa_controller
                .listar_usuarios()
            )

        except Exception as error:
            QMessageBox.warning(
                self,
                "Usuários",
                str(error),
            )
            return

        if not usuarios:
            vazio = QLabel(
                "Nenhum usuário cadastrado."
            )
            vazio.setObjectName(
                "secondaryText"
            )
            vazio.setAlignment(
                Qt.AlignCenter
            )

            self.lista.addWidget(
                vazio
            )
            return

        for usuario in usuarios:
            self.adicionar_usuario(
                usuario
            )

    def limpar_lista(
        self,
    ) -> None:
        while self.lista.count():
            item = self.lista.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def adicionar_usuario(
        self,
        usuario,
    ) -> None:
        card = QFrame()
        card.setObjectName(
            "historicoCard"
        )

        layout = QHBoxLayout(
            card
        )

        layout.setContentsMargins(
            22,
            18,
            22,
            18,
        )

        info = QVBoxLayout()

        nome = QLabel(
            str(usuario["nome"])
        )
        nome.setObjectName(
            "sectionTitle"
        )

        login = QLabel(
            f"Usuário: {usuario['usuario']}"
        )
        login.setObjectName(
            "secondaryText"
        )

        perfil = QLabel(
            f"Perfil: {usuario['perfil']}"
        )
        perfil.setObjectName(
            "secondaryText"
        )

        ativo = bool(
            usuario["ativo"]
        )

        status = QLabel(
            "● Ativo"
            if ativo
            else "● Inativo"
        )

        status.setStyleSheet(
            (
                "color: #4ADE80;"
                if ativo
                else "color: #F87171;"
            )
            + "background: transparent;"
        )

        info.addWidget(
            nome
        )

        info.addWidget(
            login
        )

        info.addWidget(
            perfil
        )

        info.addWidget(
            status
        )

        botoes = QVBoxLayout()

        editar_button = QPushButton(
            "Editar"
        )
        editar_button.setObjectName(
            "ghostButton"
        )

        editar_button.clicked.connect(
            lambda _=False, u=usuario:
                self.editar_usuario(u)
        )

        status_button = QPushButton(
            "Desativar"
            if ativo
            else "Ativar"
        )

        status_button.setObjectName(
            "ghostButton"
        )

        status_button.clicked.connect(
            lambda _=False,
            usuario_id=int(usuario["id"]),
            novo_status=not ativo:
                self.alterar_status(
                    usuario_id,
                    novo_status,
                )
        )

        botoes.addWidget(
            editar_button
        )

        botoes.addWidget(
            status_button
        )

        layout.addLayout(
            info
        )

        layout.addStretch()

        layout.addLayout(
            botoes
        )

        self.lista.addWidget(
            card
        )

    def novo_usuario(
        self,
    ) -> None:
        dialog = UsuarioDialog(
            self
        )

        if dialog.exec():
            self.carregar_usuarios()

    def editar_usuario(
        self,
        usuario,
    ) -> None:
        dialog = UsuarioDialog(
            self,
            usuario=usuario,
        )

        if dialog.exec():
            self.carregar_usuarios()

    def alterar_status(
        self,
        usuario_id: int,
        ativo: bool,
    ) -> None:
        try:
            caixa_controller.alterar_status_usuario(
                usuario_id=usuario_id,
                ativo=ativo,
            )

            self.carregar_usuarios()

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Não foi possível alterar",
                str(error),
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro",
                str(error),
            )

    def voltar(self) -> None:
        if self.on_voltar is not None:
            self.on_voltar()