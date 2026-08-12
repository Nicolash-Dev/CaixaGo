from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtCore import QDate, QSize, Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.controllers.caixa_controller import caixa_controller
from app.ui.dialogs.abrir_caixa_dialog import AbrirCaixaDialog
from app.ui.dialogs.fechar_caixa_dialog import FecharCaixaDialog
from app.ui.dialogs.movimentacao_dialog import MovimentacaoDialog
from app.ui.widgets.timeline_widget import TimelineWidget


ICONS_DIR = Path(__file__).resolve().parents[1] / "assets" / "icons"


def converter_data_sqlite_para_local(
    data_sqlite: str,
) -> datetime:
    """
    Converte uma data salva pelo SQLite em UTC
    para o horário local configurado no computador.
    """
    data_utc = datetime.fromisoformat(data_sqlite)

    if data_utc.tzinfo is None:
        data_utc = data_utc.replace(
            tzinfo=timezone.utc
        )

    return data_utc.astimezone()

def formatar_moeda(valor: float) -> str:
    texto = f"{valor:,.2f}"
    texto = (
        texto.replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
    return f"R$ {texto}"


class MetricCard(QFrame):
    def __init__(
        self,
        icon_name: str,
        title: str,
        value: str,
        detail: str,
    ) -> None:
        super().__init__()

        self.setObjectName("metricCard")
        self.setMinimumHeight(145)

        card_layout = QHBoxLayout(self)
        card_layout.setContentsMargins(26, 22, 26, 22)
        card_layout.setSpacing(20)

        icon_container = QFrame()
        icon_container.setObjectName("metricIconContainer")
        icon_container.setFixedSize(72, 72)

        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel()
        icon_label.setObjectName("metricIcon")
        icon_label.setAlignment(Qt.AlignCenter)

        icon = QIcon(str(ICONS_DIR / icon_name))
        icon_label.setPixmap(icon.pixmap(QSize(32, 32)))

        icon_layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")

        self.value_label = QLabel(value)
        self.value_label.setObjectName("metricValue")

        detail_label = QLabel(detail)
        detail_label.setObjectName("secondaryText")

        text_layout.addWidget(title_label)
        text_layout.addWidget(self.value_label)
        text_layout.addWidget(detail_label)

        card_layout.addWidget(icon_container)
        card_layout.addLayout(text_layout)
        card_layout.addStretch()

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)


class HomePage(QWidget):
    def __init__(
        self,
        on_logout,
        on_historico,
        on_configuracoes,
        on_usuarios,
    ) -> None:
        super().__init__()

        self.on_logout = on_logout
        self.on_historico = on_historico
        self.on_configuracoes = on_configuracoes
        self.on_usuarios = on_usuarios
        self.caixa_aberto_em: datetime | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(42, 34, 42, 28)
        root.setSpacing(22)

         # Cabeçalho
        header = QHBoxLayout()

        brand = QLabel("C✓  CaixaGo")
        brand.setObjectName("headerBrand")

        self.configuracoes_button = QPushButton(
            "Configurações"
        )
        self.configuracoes_button.setObjectName(
            "ghostButton"
        )
        self.configuracoes_button.clicked.connect(
            self.on_configuracoes
        )

        historico_button = QPushButton(
            "Histórico"
        )
        historico_button.setObjectName(
            "ghostButton"
        )
        historico_button.clicked.connect(
            self.on_historico
        )

        logout_button = QPushButton(
            "Sair"
        )
        logout_button.setObjectName(
            "ghostButton"
        )
        logout_button.clicked.connect(
            self.on_logout
        )
        self.usuarios_button = QPushButton(
            "Usuários"
        )

        self.usuarios_button.setObjectName(
            "ghostButton"
        )

        self.usuarios_button.clicked.connect(
            self.on_usuarios
        )

        header.addWidget(brand)
        header.addStretch()

        header.addWidget(
            self.usuarios_button
        )

        header.addWidget(
            self.configuracoes_button
        )

        header.addWidget(
            historico_button
        )

        header.addWidget(
            logout_button
        )

        # Saudação e horário
        self.greeting = QLabel("Olá")
        self.greeting.setObjectName("pageTitle")

        date_label = QLabel(
            QDate.currentDate().toString("dd/MM/yyyy")
        )
        date_label.setObjectName("secondaryText")

        self.clock_label = QLabel()
        self.clock_label.setObjectName("metricValue")

        self.duration_label = QLabel()
        self.duration_label.setObjectName("secondaryText")

        self.status_label = QLabel()
        self.status_label.setObjectName("warningBadge")

        # Cards
        metrics = QGridLayout()
        metrics.setHorizontalSpacing(20)
        metrics.setVerticalSpacing(20)

        self.faturamento_card = MetricCard(
            "faturamento.svg",
            "Faturamento",
            "R$ 0,00",
            "Total de vendas",
        )

        self.dinheiro_card = MetricCard(
            "dinheiro.svg",
            "Dinheiro",
            "R$ 0,00",
            "Saldo esperado no caixa",
        )

        self.eventos_card = MetricCard(
            "eventos.svg",
            "Eventos",
            "0",
            "Movimentações registradas",
        )

        metrics.addWidget(self.faturamento_card, 0, 0)
        metrics.addWidget(self.dinheiro_card, 0, 1)
        metrics.addWidget(self.eventos_card, 0, 2)

        # Painel GO
        go_card = QFrame()
        go_card.setObjectName("goCard")

        go_layout = QVBoxLayout(go_card)
        go_layout.setContentsMargins(28, 22, 28, 22)
        go_layout.setSpacing(8)

        go_title = QLabel("GO")
        go_title.setObjectName("goTitle")

        self.go_message = QLabel()
        self.go_message.setObjectName("secondaryText")
        self.go_message.setWordWrap(True)

        go_layout.addWidget(go_title)
        go_layout.addWidget(self.go_message)

        # Timeline
        self.timeline = TimelineWidget()

        # Botões de movimentação
        self.actions_layout = QHBoxLayout()
        self.actions_layout.setSpacing(12)

        self.venda_button = QPushButton("Venda")
        self.venda_button.setObjectName("primaryButton")
        self.venda_button.setIcon(
            QIcon(str(ICONS_DIR / "venda.svg"))
        )
        self.venda_button.setIconSize(QSize(24, 24))
        self.venda_button.clicked.connect(
            lambda: self.abrir_movimentacao("VENDA")
        )

        self.sangria_button = QPushButton("Sangria")
        self.sangria_button.setObjectName("ghostButton")
        self.sangria_button.setIcon(
            QIcon(str(ICONS_DIR / "sangria.svg"))
        )
        self.sangria_button.setIconSize(QSize(24, 24))
        self.sangria_button.clicked.connect(
            lambda: self.abrir_movimentacao("SANGRIA")
        )

        self.suprimento_button = QPushButton("Suprimento")
        self.suprimento_button.setObjectName("ghostButton")
        self.suprimento_button.setIcon(
            QIcon(str(ICONS_DIR / "suprimento.svg"))
        )
        self.suprimento_button.setIconSize(QSize(24, 24))
        self.suprimento_button.clicked.connect(
            lambda: self.abrir_movimentacao("SUPRIMENTO")
        )

        self.actions_layout.addWidget(self.venda_button)
        self.actions_layout.addWidget(self.sangria_button)
        self.actions_layout.addWidget(self.suprimento_button)

        # Botão principal: abre ou fecha o caixa
        self.main_action_button = QPushButton("Abrir Caixa")
        self.main_action_button.setObjectName("primaryButton")
        self.main_action_button.clicked.connect(
            self.executar_acao_principal
        )

        # Montagem da tela
        root.addLayout(header)
        root.addWidget(self.greeting)
        root.addWidget(date_label)
        root.addWidget(self.clock_label)
        root.addWidget(self.duration_label)
        root.addWidget(self.status_label)
        root.addLayout(metrics)
        root.addWidget(go_card)
        root.addWidget(self.timeline)
        root.addSpacing(6)
        root.addLayout(self.actions_layout)
        root.addStretch()
        root.addWidget(self.main_action_button)

        # Relógio em tempo real
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.atualizar_relogio)
        self.timer.start(1000)

        self.atualizar_home()
        self.atualizar_relogio()

    def executar_acao_principal(self) -> None:
        caixa = caixa_controller.obter_caixa_aberto()

        if caixa is None:
            self.abrir_caixa()
        else:
            self.fechar_caixa()

    def abrir_caixa(self) -> None:
        dialog = AbrirCaixaDialog(self)

        if dialog.exec():
            self.atualizar_home()
            self.atualizar_relogio()

    def fechar_caixa(self) -> None:
        try:
            dialog = FecharCaixaDialog(self)

            if dialog.exec():
                self.atualizar_home()
                self.atualizar_relogio()

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Não foi possível fechar o caixa",
                str(error),
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro no fechamento",
                f"Ocorreu um problema inesperado:\n{error}",
            )

    def abrir_movimentacao(self, tipo: str) -> None:
        dialog = MovimentacaoDialog(
            parent=self,
            tipo_inicial=tipo,
        )

        if dialog.exec():
            self.atualizar_home()

    def atualizar_relogio(self) -> None:
        agora = datetime.now().astimezone()

        self.clock_label.setText(
            agora.strftime("%H:%M:%S")
        )

        if self.caixa_aberto_em is None:
            self.duration_label.setText(
                "Nenhum caixa aberto no momento"
            )
            return

        duracao = agora - self.caixa_aberto_em
        segundos_totais = max(
            0,
            int(duracao.total_seconds()),
        )

        horas, restante = divmod(
            segundos_totais,
            3600,
        )
        minutos, segundos = divmod(
            restante,
            60,
        )

        self.duration_label.setText(
            "Tempo de caixa aberto: "
            f"{horas:02d}h "
            f"{minutos:02d}min "
            f"{segundos:02d}s"
        )

    def atualizar_home(self) -> None:
        usuario = caixa_controller.obter_usuario_logado()

        if usuario is not None:
            perfil = str(
                usuario.get(
                    "perfil",
                    ""
                )
            ).upper()

            eh_gerente = (
                perfil == "GERENTE"
            )

            self.usuarios_button.setVisible(
                eh_gerente
            )

            self.configuracoes_button.setVisible(
                eh_gerente
            )

            nome = str(
                usuario.get(
                    "nome",
                    "Usuário"
                )
            )

            hora = datetime.now().hour

            if hora < 12:
                saudacao = "Bom dia"
            elif hora < 18:
                saudacao = "Boa tarde"
            else:
                saudacao = "Boa noite"

            self.greeting.setText(
                f"{saudacao}, {nome}"
            )

        else:
            self.usuarios_button.hide()
            self.configuracoes_button.hide()
            self.greeting.setText(
                "Olá"
            )

        caixa = caixa_controller.obter_caixa_aberto()

        if caixa is None:
            self.configurar_home_caixa_fechado()
            return

        self.configurar_home_caixa_aberto(
            caixa
        )

    def configurar_home_caixa_fechado(self) -> None:
        self.caixa_aberto_em = None

        self.status_label.setText("● Caixa fechado")

        self.faturamento_card.set_value("R$ 0,00")
        self.dinheiro_card.set_value("R$ 0,00")
        self.eventos_card.set_value("0")

        self.go_message.setText(
            "Tudo pronto para começar. "
            "Abra o caixa para iniciar o expediente."
        )

        self.main_action_button.setText("Abrir Caixa")
        self.main_action_button.setIcon(QIcon())
        self.main_action_button.setEnabled(True)

        self.definir_acoes_habilitadas(False)
        self.timeline.mostrar_vazio()

    def configurar_home_caixa_aberto(self, caixa) -> None:
        aberto_em = converter_data_sqlite_para_local(
            str(caixa["aberto_em"])
        )

        self.caixa_aberto_em = aberto_em
        horario = aberto_em.strftime("%H:%M")

        resumo = caixa_controller.obter_resumo()

        self.status_label.setText(
            f"● Caixa aberto desde {horario}"
        )

        self.faturamento_card.set_value(
            formatar_moeda(resumo["faturamento"])
        )

        self.dinheiro_card.set_value(
            formatar_moeda(resumo["saldo_esperado"])
        )

        self.eventos_card.set_value(
            str(resumo["quantidade"])
        )

        self.go_message.setText(
            "Caixa operando normalmente. "
            f"Foram registradas {resumo['quantidade']} "
            "movimentações e o saldo esperado é "
            f"{formatar_moeda(resumo['saldo_esperado'])}."
        )

        self.main_action_button.setText("Fechar Caixa")
        self.main_action_button.setIcon(
            QIcon(str(ICONS_DIR / "fechar_caixa.svg"))
        )
        self.main_action_button.setIconSize(
            QSize(24, 24)
        )
        self.main_action_button.setEnabled(True)

        self.definir_acoes_habilitadas(True)

        movimentacoes = (
            caixa_controller.obter_ultimas_movimentacoes(
                limite=5,
            )
        )

        self.timeline.atualizar(movimentacoes)

    def definir_acoes_habilitadas(
        self,
        habilitado: bool,
    ) -> None:
        self.venda_button.setEnabled(habilitado)
        self.sangria_button.setEnabled(habilitado)
        self.suprimento_button.setEnabled(habilitado)