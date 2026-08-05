from PySide6.QtWidgets import QMainWindow, QStackedWidget

from app.ui.login_page import LoginPage
from app.ui.home_page import HomePage


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("CaixaGo")
        self.resize(1180, 760)
        self.setMinimumSize(980, 640)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_page = LoginPage(on_login_success=self.show_home)
        self.home_page = HomePage(on_logout=self.show_login)

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.home_page)
        self.show_login()

    def show_login(self) -> None:
        self.stack.setCurrentWidget(self.login_page)
        self.login_page.reset_pin()

    def show_home(self) -> None:
        self.stack.setCurrentWidget(self.home_page)
