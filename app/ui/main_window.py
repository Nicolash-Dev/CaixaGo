from PySide6.QtWidgets import QMainWindow, QStackedWidget

from app.ui.home_page import HomePage
from app.ui.historico_caixas_page import HistoricoCaixasPage
from app.ui.login_page import LoginPage


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
            on_logout=self.show_login,
            on_historico=self.show_historico,
        )

        self.historico_page = HistoricoCaixasPage(
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

        self.show_login()

    def show_login(self) -> None:
        self.stack.setCurrentWidget(
            self.login_page
        )

        self.login_page.reset_pin()

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