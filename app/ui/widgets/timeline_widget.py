from datetime import datetime, timezone

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


def formatar_moeda(valor: float) -> str:
    texto = f"{valor:,.2f}"
    texto = (
        texto.replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
    return f"R$ {texto}"


def converter_horario_local(data_sqlite: str) -> str:
    try:
        data_utc = datetime.fromisoformat(data_sqlite)

        if data_utc.tzinfo is None:
            data_utc = data_utc.replace(tzinfo=timezone.utc)

        return data_utc.astimezone().strftime("%H:%M")

    except (TypeError, ValueError):
        return "--:--"


class TimelineWidget(QFrame):
    def __init__(self) -> None:
        super().__init__()

        self.setObjectName("timelineCard")
        self.setMinimumHeight(185)
        self.setMaximumHeight(230)

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(28, 22, 28, 22)
        layout_principal.setSpacing(14)

        titulo = QLabel("Últimas movimentações")
        titulo.setObjectName("sectionTitle")

        layout_principal.addWidget(titulo)

        # Área rolável da Timeline
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )
        self.scroll_area.setMinimumHeight(105)
        self.scroll_area.setMaximumHeight(145)

        self.conteudo = QWidget()
        self.conteudo.setObjectName("timelineContent")

        self.lista = QVBoxLayout(self.conteudo)
        self.lista.setContentsMargins(0, 0, 0, 0)
        self.lista.setSpacing(10)
        self.lista.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.conteudo)
        layout_principal.addWidget(self.scroll_area)

        self.mostrar_vazio()

    def limpar(self) -> None:
        while self.lista.count():
            item = self.lista.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def mostrar_vazio(self) -> None:
        self.limpar()

        texto = QLabel(
            "Nenhuma movimentação registrada."
        )
        texto.setObjectName("secondaryText")
        texto.setMinimumHeight(30)

        self.lista.addWidget(texto)

    def atualizar(self, movimentacoes) -> None:
        self.limpar()

        if not movimentacoes:
            self.mostrar_vazio()
            return

        for movimentacao in movimentacoes:
            tipo = str(
                movimentacao["tipo"]
            ).upper()

            valor = float(
                movimentacao["valor"]
            )

            criado_em = str(
                movimentacao["criado_em"]
            )

            horario = converter_horario_local(
                criado_em
            )

            if tipo == "VENDA":
                descricao = "Venda"
                sinal = "+"
                cor_valor = "#4ADE80"

            elif tipo == "SUPRIMENTO":
                descricao = "Suprimento"
                sinal = "+"
                cor_valor = "#4ADE80"

            elif tipo == "SANGRIA":
                descricao = "Sangria"
                sinal = "-"
                cor_valor = "#F87171"

            else:
                descricao = tipo.title()
                sinal = ""
                cor_valor = "#F8FAFC"

            linha = QFrame()
            linha.setObjectName("timelineRow")
            linha.setFixedHeight(48)

            linha_layout = QHBoxLayout(linha)
            linha_layout.setContentsMargins(
                16,
                8,
                16,
                8,
            )
            linha_layout.setSpacing(14)

            horario_label = QLabel(horario)
            horario_label.setFixedWidth(60)
            horario_label.setStyleSheet(
                """
                color: #94A3B8;
                background-color: transparent;
                font-size: 14px;
                """
            )

            descricao_label = QLabel(descricao)
            descricao_label.setStyleSheet(
                """
                color: #F8FAFC;
                background-color: transparent;
                font-size: 14px;
                font-weight: 700;
                """
            )

            valor_label = QLabel(
                f"{sinal}{formatar_moeda(valor)}"
            )
            valor_label.setAlignment(
                Qt.AlignRight | Qt.AlignVCenter
            )
            valor_label.setStyleSheet(
                f"""
                color: {cor_valor};
                background-color: transparent;
                font-size: 14px;
                font-weight: 800;
                """
            )

            linha_layout.addWidget(horario_label)
            linha_layout.addWidget(descricao_label)
            linha_layout.addStretch()
            linha_layout.addWidget(valor_label)

            self.lista.addWidget(linha)

        self.lista.addStretch()