from datetime import datetime, timezone

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.controllers.caixa_controller import caixa_controller
from app.reports.fechamento_pdf import gerar_pdf_fechamento


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


def converter_horario_local(
    data_sqlite: str | None,
) -> str:
    if not data_sqlite:
        return "--:--"

    try:
        data = datetime.fromisoformat(
            data_sqlite
        )

        if data.tzinfo is None:
            data = data.replace(
                tzinfo=timezone.utc
            )

        data = data.astimezone()

        return data.strftime("%H:%M")

    except (TypeError, ValueError):
        return "--:--"


class DetalhesCaixaPage(QWidget):
    def __init__(
        self,
        on_voltar=None,
    ) -> None:
        super().__init__()

        self.on_voltar = on_voltar
        self.caixa_id_atual = None

        self.criar_interface()

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

        self.titulo = QLabel(
            "Detalhes do Caixa"
        )
        self.titulo.setObjectName(
            "pageTitle"
        )

        self.subtitulo = QLabel(
            "Consulte todas as informações "
            "do expediente."
        )
        self.subtitulo.setObjectName(
            "secondaryText"
        )

        titulo_container.addWidget(
            self.titulo
        )

        titulo_container.addWidget(
            self.subtitulo
        )

        pdf_button = QPushButton(
            "Gerar PDF"
        )
        pdf_button.setObjectName(
            "primaryButton"
        )
        pdf_button.setFixedWidth(
            140
        )
        pdf_button.clicked.connect(
            self.gerar_pdf
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
            pdf_button
        )

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

        self.conteudo = QVBoxLayout(
            self.container
        )

        self.conteudo.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.conteudo.setSpacing(
            16
        )

        self.conteudo.setAlignment(
            Qt.AlignTop
        )

        self.scroll.setWidget(
            self.container
        )

        root.addWidget(
            self.scroll
        )

    def limpar(self) -> None:
        while self.conteudo.count():
            item = self.conteudo.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def carregar_caixa(
        self,
        caixa_id: int,
    ) -> None:
        self.caixa_id_atual = caixa_id

        self.limpar()

        detalhes = (
            caixa_controller
            .obter_detalhes_caixa(
                caixa_id
            )
        )

        caixa = detalhes["caixa"]
        resumo = detalhes["resumo"]
        movimentacoes = detalhes["movimentacoes"]

        self.titulo.setText(
            f"Caixa #{caixa['id']}"
        )

        self.subtitulo.setText(
            f"Operador: {caixa['operador']}"
        )

        # Card do expediente
        expediente_card = QFrame()
        expediente_card.setObjectName(
            "historicoCard"
        )

        expediente_layout = QVBoxLayout(
            expediente_card
        )

        expediente_layout.setContentsMargins(
            22,
            18,
            22,
            18,
        )

        expediente_layout.setSpacing(8)

        expediente_titulo = QLabel(
            "Resumo do expediente"
        )
        expediente_titulo.setObjectName(
            "sectionTitle"
        )

        periodo = QLabel(
            "Abertura: "
            f"{converter_data_local(caixa['aberto_em'])}\n"
            "Fechamento: "
            f"{converter_data_local(caixa['fechado_em'])}"
        )

        periodo.setObjectName(
            "secondaryText"
        )

        expediente_layout.addWidget(
            expediente_titulo
        )

        expediente_layout.addWidget(
            periodo
        )

        self.conteudo.addWidget(
            expediente_card
        )

        # Card financeiro
        financeiro_card = QFrame()
        financeiro_card.setObjectName(
            "historicoCard"
        )

        financeiro_layout = QVBoxLayout(
            financeiro_card
        )

        financeiro_layout.setContentsMargins(
            22,
            18,
            22,
            18,
        )

        financeiro_layout.setSpacing(10)

        financeiro_titulo = QLabel(
            "Resumo financeiro"
        )
        financeiro_titulo.setObjectName(
            "sectionTitle"
        )

        financeiro_layout.addWidget(
            financeiro_titulo
        )

        linhas = [
            (
                "Valor inicial",
                float(caixa["valor_inicial"]),
            ),
            (
                "Faturamento",
                float(resumo["faturamento"]),
            ),
            (
                "Dinheiro",
                float(resumo["vendas_dinheiro"]),
            ),
            (
                "PIX",
                float(resumo["vendas_pix"]),
            ),
            (
                "Débito",
                float(resumo["vendas_debito"]),
            ),
            (
                "Crédito",
                float(resumo["vendas_credito"]),
            ),
            (
                "Sangrias",
                float(resumo["sangrias"]),
            ),
            (
                "Suprimentos",
                float(resumo["suprimentos"]),
            ),
            (
                "Saldo esperado",
                float(resumo["saldo_esperado"]),
            ),
        ]

        for descricao, valor in linhas:
            linha = QHBoxLayout()

            descricao_label = QLabel(
                descricao
            )
            descricao_label.setObjectName(
                "secondaryText"
            )

            valor_label = QLabel(
                formatar_moeda(valor)
            )

            valor_label.setStyleSheet(
                """
                color: #F8FAFC;
                background-color: transparent;
                font-weight: 700;
                """
            )

            linha.addWidget(
                descricao_label
            )

            linha.addStretch()

            linha.addWidget(
                valor_label
            )

            financeiro_layout.addLayout(
                linha
            )

        self.conteudo.addWidget(
            financeiro_card
        )

        # Card de movimentações
        movimentacoes_card = QFrame()
        movimentacoes_card.setObjectName(
            "historicoCard"
        )

        movimentacoes_layout = QVBoxLayout(
            movimentacoes_card
        )

        movimentacoes_layout.setContentsMargins(
            22,
            18,
            22,
            18,
        )

        movimentacoes_layout.setSpacing(10)

        movimentacoes_titulo = QLabel(
            "Movimentações"
        )
        movimentacoes_titulo.setObjectName(
            "sectionTitle"
        )

        movimentacoes_layout.addWidget(
            movimentacoes_titulo
        )

        if not movimentacoes:
            vazio = QLabel(
                "Nenhuma movimentação registrada."
            )

            vazio.setObjectName(
                "secondaryText"
            )

            movimentacoes_layout.addWidget(
                vazio
            )

        else:
            for movimentacao in movimentacoes:
                self.adicionar_movimentacao(
                    movimentacoes_layout,
                    movimentacao
                )

        self.conteudo.addWidget(
            movimentacoes_card
        )

    def adicionar_movimentacao(
        self,
        layout: QVBoxLayout,
        movimentacao: dict,
    ) -> None:
        tipo = str(
            movimentacao["tipo"]
        ).upper()

        valor = float(
            movimentacao["valor"]
        )

        forma = (
            movimentacao
            .get("forma_pagamento")
        )

        descricao = str(
            movimentacao.get(
                "descricao"
            ) or ""
        ).strip()

        horario = converter_horario_local(
            movimentacao.get(
                "criado_em"
            )
        )

        if tipo == "VENDA":
            titulo = "Venda"

            if forma:
                titulo += (
                    f" • {forma.title()}"
                )

            sinal = "+"
            cor = "#4ADE80"

        elif tipo == "SANGRIA":
            titulo = "Sangria"
            sinal = "-"
            cor = "#F87171"

        elif tipo == "SUPRIMENTO":
            titulo = "Suprimento"
            sinal = "+"
            cor = "#4ADE80"

        else:
            titulo = tipo.title()
            sinal = ""
            cor = "#F8FAFC"

        linha = QFrame()
        linha.setObjectName(
            "timelineRow"
        )

        linha_layout = QHBoxLayout(
            linha
        )

        linha_layout.setContentsMargins(
            16,
            10,
            16,
            10,
        )

        horario_label = QLabel(
            horario
        )
        horario_label.setObjectName(
            "secondaryText"
        )
        horario_label.setFixedWidth(
            60
        )

        texto_container = QVBoxLayout()

        titulo_label = QLabel(
            titulo
        )
        titulo_label.setStyleSheet(
            """
            color: #F8FAFC;
            background-color: transparent;
            font-weight: 700;
            """
        )

        texto_container.addWidget(
            titulo_label
        )

        if descricao:
            descricao_label = QLabel(
                descricao
            )

            descricao_label.setObjectName(
                "secondaryText"
            )

            texto_container.addWidget(
                descricao_label
            )

        valor_label = QLabel(
            f"{sinal}{formatar_moeda(valor)}"
        )

        valor_label.setStyleSheet(
            f"""
            color: {cor};
            background-color: transparent;
            font-weight: 800;
            """
        )

        linha_layout.addWidget(
            horario_label
        )

        linha_layout.addLayout(
            texto_container
        )

        linha_layout.addStretch()

        linha_layout.addWidget(
            valor_label
        )

        layout.addWidget(
            linha
        )

    def gerar_pdf(self) -> None:
        if self.caixa_id_atual is None:
            QMessageBox.warning(
                self,
                "PDF",
                "Nenhum caixa foi selecionado.",
            )
            return

        try:
            detalhes = (
                caixa_controller
                .obter_detalhes_caixa(
                    self.caixa_id_atual
                )
            )

            arquivo = gerar_pdf_fechamento(
                detalhes
            )

            QMessageBox.information(
                self,
                "PDF gerado",
                (
                    "Relatório gerado com sucesso!\n\n"
                    f"Arquivo:\n{arquivo}"
                ),
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro ao gerar PDF",
                (
                    "Não foi possível gerar "
                    "o relatório.\n\n"
                    f"Erro: {error}"
                ),
            )

    def voltar(self) -> None:
        if self.on_voltar is not None:
            self.on_voltar()