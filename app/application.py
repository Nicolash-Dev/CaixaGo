from PySide6.QtWidgets import QApplication

from app.config import APP_NAME
from app.database.database import database
from app.ui.main_window import MainWindow
from app.ui.splash_screen import SplashScreen
from app.utils.styles import GLOBAL_STYLESHEET


def create_application() -> QApplication:
    app = QApplication([])
    app.setApplicationName(APP_NAME)
    app.setStyleSheet(GLOBAL_STYLESHEET)

    database.initialize()

    main_window = MainWindow()

    splash = SplashScreen(
        on_finished=main_window.show
    )

    splash.show()

    # Mantém as referências em memória.
    app.main_window = main_window
    app.splash = splash

    return app