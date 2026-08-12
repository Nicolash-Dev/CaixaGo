from datetime import datetime, timezone

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.controllers.caixa_controller import caixa_controller


def formatar_moeda(valor: float) -> str:
    texto = f"{valor:,.2f}"
    texto = (
        texto.replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {texto}"


def converter_data_local(
    data_sqlite: str | None,
) -> str:
    if not data_sqlite:
        return "--"

    try:
        data = datetime.fromisoformat(
            data_sqlite
        )

        if data.tzinfo is None:
            data = data.replace(
                tzinfo=timezone.utc
            )

        data = data.astimezone()

        return data.strftime(
            "%d/%m/%Y às %H:%M"
        )

    except (TypeError, ValueError):
        return "--"


class HistoricoCaixasPage(QWidget):
    def __init__(
        self,
        on_voltar=None,
        on_abrir_caixa=None,
    ) -> None:
        super().__init__()

        self.on_voltar = on_voltar
        self.on_abrir_caixa = on_abrir_caixa

        self.criar_interface()
        self.carregar_historico()

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
            "Histórico de Caixas"
        )
        titulo.setObjectName(
            "pageTitle"
        )

        subtitulo = QLabel(
            "Consulte os expedientes "
            "encerrados anteriormente."
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

        # Área rolável
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

    def limpar_lista(self) -> None:
        while self.lista.count():
            item = self.lista.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def carregar_historico(self) -> None:
        self.limpar_lista()

        caixas = (
            caixa_controller
            .listar_caixas_fechados(
                limite=50
            )
        )

        if not caixas:
            vazio = QLabel(
                "Nenhum caixa fechado "
                "foi encontrado."
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

        for caixa in caixas:
            self.adicionar_caixa(
                caixa
            )

    def adicionar_caixa(
        self,
        caixa,
    ) -> None:
        card = QFrame()
        card.setObjectName(
            "historicoCard"
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            22,
            18,
            22,
            18,
        )

        layout.setSpacing(
            12
        )

        # Primeira linha
        topo = QHBoxLayout()

        caixa_id = QLabel(
            f"Caixa #{caixa['id']}"
        )

        caixa_id.setObjectName(
            "sectionTitle"
        )

        operador = QLabel(
            f"Operador: "
            f"{caixa['operador']}"
        )

        operador.setObjectName(
            "secondaryText"
        )

        faturamento = QLabel(
            formatar_moeda(
                float(
                    caixa["faturamento"]
                )
            )
        )

        faturamento.setObjectName(
            "metricValue"
        )

        faturamento.setAlignment(
            Qt.AlignRight
        )

        topo.addWidget(
            caixa_id
        )

        topo.addWidget(
            operador
        )

        topo.addStretch()

        topo.addWidget(
            faturamento
        )

        layout.addLayout(
            topo
        )

        # Horários
        horarios = QLabel(
            "Abertura: "
            f"{converter_data_local(caixa['aberto_em'])}"
            "    •    "
            "Fechamento: "
            f"{converter_data_local(caixa['fechado_em'])}"
        )

        horarios.setObjectName(
            "secondaryText"
        )

        layout.addWidget(
            horarios
        )

        # Formas de pagamento
        pagamentos = QLabel(
            "Dinheiro: "
            f"{formatar_moeda(float(caixa['vendas_dinheiro']))}"
            "    |    PIX: "
            f"{formatar_moeda(float(caixa['vendas_pix']))}"
            "    |    Débito: "
            f"{formatar_moeda(float(caixa['vendas_debito']))}"
            "    |    Crédito: "
            f"{formatar_moeda(float(caixa['vendas_credito']))}"
        )

        pagamentos.setWordWrap(
            True
        )

        pagamentos.setStyleSheet(
            """
            color: #F8FAFC;
            background-color: transparent;
            """
        )

        layout.addWidget(
            pagamentos
        )

        # Rodapé
        rodape = QLabel(
            f"{caixa['quantidade_eventos']} eventos"
            "    •    "
            "Sangrias: "
            f"{formatar_moeda(float(caixa['sangrias']))}"
            "    •    "
            "Suprimentos: "
            f"{formatar_moeda(float(caixa['suprimentos']))}"
        )

        rodape.setObjectName(
            "secondaryText"
        )

        layout.addWidget(
            rodape
        )

        detalhes_button = QPushButton(
            "Ver detalhes"
        )

        detalhes_button.setObjectName(
            "ghostButton"
        )

        detalhes_button.clicked.connect(
            lambda _=False, caixa_id=int(caixa["id"]):
                self.abrir_detalhes(caixa_id)
        )

        layout.addWidget(
            detalhes_button
        )

        self.lista.addWidget(
            card
        )

    def abrir_detalhes(
        self,
        caixa_id: int,
    ) -> None:
        if self.on_abrir_caixa is not None:
            self.on_abrir_caixa(
                caixa_id
            )

    def voltar(self) -> None:
        if self.on_voltar is not None:
            self.on_voltar()