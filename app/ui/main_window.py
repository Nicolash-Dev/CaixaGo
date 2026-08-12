from PySide6.QtWidgets import QMainWindow, QStackedWidget

from app.controllers.caixa_controller import caixa_controller
from app.ui.configuracoes_page import ConfiguracoesPage
from app.ui.detalhes_caixa_page import DetalhesCaixaPage
from app.ui.historico_caixas_page import HistoricoCaixasPage
from app.ui.home_page import HomePage
from app.ui.login_page import LoginPage
from app.ui.usuarios_page import UsuariosPage


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("CaixaGo")
        self.resize(1180, 760)
        self.setMinimumSize(980, 640)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_page = LoginPage(
            on_login_success=self.show_home
        )

        self.home_page = HomePage(
            on_logout=self.fazer_logout,
            on_historico=self.show_historico,
            on_configuracoes=self.show_configuracoes,
            on_usuarios=self.show_usuarios,
        )

        self.historico_page = HistoricoCaixasPage(
            on_voltar=self.show_home,
            on_abrir_caixa=self.show_detalhes_caixa,
        )

        self.detalhes_caixa_page = DetalhesCaixaPage(
            on_voltar=self.show_historico
        )

        self.configuracoes_page = ConfiguracoesPage(
            on_voltar=self.show_home
        )

        self.usuarios_page = UsuariosPage(
            on_voltar=self.show_home
        )

        self.stack.addWidget(
            self.login_page
        )

        self.stack.addWidget(
            self.home_page
        )

        self.stack.addWidget(
            self.historico_page
        )

        self.stack.addWidget(
            self.detalhes_caixa_page
        )

        self.stack.addWidget(
            self.configuracoes_page
        )

        self.stack.addWidget(
            self.usuarios_page
        )

        self.show_login()

    def show_login(self) -> None:
        self.login_page.reset_pin()

        self.stack.setCurrentWidget(
            self.login_page
        )

    def fazer_logout(self) -> None:
        caixa_controller.logout()

        self.login_page.reset_pin()

        self.stack.setCurrentWidget(
            self.login_page
        )

    def show_home(self) -> None:
        self.home_page.atualizar_home()

        self.stack.setCurrentWidget(
            self.home_page
        )

    def show_historico(self) -> None:
        self.historico_page.carregar_historico()

        self.stack.setCurrentWidget(
            self.historico_page
        )

    def show_detalhes_caixa(
        self,
        caixa_id: int,
    ) -> None:
        self.detalhes_caixa_page.carregar_caixa(
            caixa_id
        )

        self.stack.setCurrentWidget(
            self.detalhes_caixa_page
        )

    def show_configuracoes(self) -> None:
        self.configuracoes_page.carregar_configuracoes()

        self.stack.setCurrentWidget(
            self.configuracoes_page
        )

    def show_usuarios(self) -> None:
        self.usuarios_page.carregar_usuarios()

        self.stack.setCurrentWidget(
            self.usuarios_page
        )