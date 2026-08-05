from datetime import datetime

from PySide6.QtCore import QDate, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QGridLayout,
)

from app.controllers.caixa_controller import caixa_controller
from app.ui.abrir_caixa_dialog import AbrirCaixaDialog


def formatar_moeda(valor: float) -> str:
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


class MetricCard(QFrame):
    def __init__(self, title: str, value: str, detail: str) -> None:
        super().__init__()
        self.setObjectName("metricCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")

        self.value_label = QLabel(value)
        self.value_label.setObjectName("metricValue")

        detail_label = QLabel(detail)
        detail_label.setObjectName("secondaryText")

        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(detail_label)

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)


class HomePage(QWidget):
    def __init__(self, on_logout) -> None:
        super().__init__()

        self.on_logout = on_logout

        root = QVBoxLayout(self)
        root.setContentsMargins(34, 28, 34, 28)
        root.setSpacing(24)

        header = QHBoxLayout()

        brand = QLabel("C✓  CaixaGo")
        brand.setObjectName("headerBrand")

        logout_button = QPushButton("Sair")
        logout_button.setObjectName("ghostButton")
        logout_button.clicked.connect(self.on_logout)

        header.addWidget(brand)
        header.addStretch()
        header.addWidget(logout_button)

        greeting = QLabel("Bom dia, Nicolas")
        greeting.setObjectName("pageTitle")

        date_text = QDate.currentDate().toString("dd/MM/yyyy")
        date_label = QLabel(date_text)
        date_label.setObjectName("secondaryText")

        self.clock_label = QLabel()
        self.clock_label.setObjectName("metricValue")

        self.duration_label = QLabel()
        self.duration_label.setObjectName("secondaryText")

        self.status_label = QLabel()
        self.status_label.setObjectName("warningBadge")

        metrics = QGridLayout()
        metrics.setSpacing(18)

        self.faturamento_card = MetricCard(
            "Faturamento",
            "R$ 0,00",
            "Hoje",
        )

        self.dinheiro_card = MetricCard(
            "Dinheiro",
            "R$ 0,00",
            "Disponível no caixa",
        )

        self.eventos_card = MetricCard(
            "Eventos",
            "0",
            "Movimentações registradas",
        )

        metrics.addWidget(self.faturamento_card, 0, 0)
        metrics.addWidget(self.dinheiro_card, 0, 1)
        metrics.addWidget(self.eventos_card, 0, 2)

        go_card = QFrame()
        go_card.setObjectName("goCard")

        go_layout = QVBoxLayout(go_card)
        go_layout.setContentsMargins(24, 20, 24, 20)

        go_title = QLabel("GO")
        go_title.setObjectName("goTitle")

        self.go_message = QLabel()
        self.go_message.setWordWrap(True)
        self.go_message.setObjectName("secondaryText")

        go_layout.addWidget(go_title)
        go_layout.addWidget(self.go_message)

        self.open_cash_button = QPushButton("Abrir Caixa")
        self.open_cash_button.setObjectName("primaryButton")
        self.open_cash_button.clicked.connect(self.abrir_caixa)

        root.addLayout(header)
        root.addSpacing(8)
        root.addWidget(greeting)
        root.addWidget(date_label)
        root.addWidget(self.clock_label)
        root.addWidget(self.duration_label)
        root.addWidget(self.status_label)
        root.addLayout(metrics)
        root.addWidget(go_card)
        root.addStretch()
        root.addWidget(self.open_cash_button)

        self.caixa_aberto_em = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.atualizar_relogio)
        self.timer.start(1000)
        self.atualizar_home()
        self.atualizar_relogio()

    def abrir_caixa(self) -> None:
        dialog = AbrirCaixaDialog(self)

        if dialog.exec():
            self.atualizar_home()
    def atualizar_relogio(self) -> None:
        agora = datetime.now()

        self.clock_label.setText(
        agora.strftime("%H:%M:%S")
        )

        if self.caixa_aberto_em is None:
            self.duration_label.setText(
            "Nenhum caixa aberto no momento"
        )
        return

        duracao = agora - self.caixa_aberto_em
        segundos_totais = max(0, int(duracao.total_seconds()))

        horas, restante = divmod(segundos_totais, 3600)
        minutos, segundos = divmod(restante, 60)

        self.duration_label.setText(
            f"Tempo de caixa aberto: "
            f"{horas:02d}h {minutos:02d}min {segundos:02d}s"
        )
    def atualizar_home(self) -> None:
        caixa = caixa_controller.obter_caixa_aberto()

        if caixa is None:
            self.caixa_aberto_em = None

            self.status_label.setText("● Caixa fechado")
            self.dinheiro_card.set_value("R$ 0,00")
            self.go_message.setText(
                "Tudo pronto para começar. "
                "Abra o caixa para iniciar o expediente."
            )
            self.open_cash_button.setText("Abrir Caixa")
            self.open_cash_button.setEnabled(True)
            return

        valor_inicial = float(caixa["valor_inicial"])
        aberto_em = datetime.fromisoformat(caixa["aberto_em"])
        self.caixa_aberto_em = aberto_em
        horario = aberto_em.strftime("%H:%M")

        self.status_label.setText(
            f"● Caixa aberto desde {horario}"
        )

        self.dinheiro_card.set_value(
            formatar_moeda(valor_inicial)
        )

        self.go_message.setText(
            f"Bom trabalho, Nicolas! O caixa foi aberto às "
            f"{horario}, com valor inicial de "
            f"{formatar_moeda(valor_inicial)}."
        )

        self.open_cash_button.setText("Caixa já está aberto")
        self.open_cash_button.setEnabled(False)