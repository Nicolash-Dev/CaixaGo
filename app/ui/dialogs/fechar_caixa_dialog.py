from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.controllers.caixa_controller import caixa_controller


def formatar_moeda(valor: float) -> str:
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


class FecharCaixaDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Fechar Caixa")
        self.setModal(True)
        self.setMinimumWidth(520)

        caixa = caixa_controller.obter_caixa_aberto()

        if caixa is None:
            raise ValueError("Não existe um caixa aberto.")

        self.resumo = caixa_controller.obter_resumo()
        self.valor_esperado = float(self.resumo["saldo_esperado"])

        aberto_em = datetime.fromisoformat(caixa["aberto_em"])
        agora = datetime.now()
        duracao = agora - aberto_em

        segundos = max(0, int(duracao.total_seconds()))
        horas, restante = divmod(segundos, 3600)
        minutos, _ = divmod(restante, 60)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 30, 32, 30)
        layout.setSpacing(18)

        titulo = QLabel("Fechamento de Caixa")
        titulo.setObjectName("pageTitle")

        subtitulo = QLabel(
            "Confira os valores antes de encerrar o expediente."
        )
        subtitulo.setObjectName("secondaryText")

        informacoes = QFrame()
        informacoes.setObjectName("goCard")

        info_layout = QVBoxLayout(informacoes)
        info_layout.setContentsMargins(22, 18, 22, 18)
        info_layout.setSpacing(8)

        info_layout.addWidget(
            QLabel(f"Abertura: {aberto_em.strftime('%d/%m/%Y às %H:%M')}")
        )
        info_layout.addWidget(
            QLabel(f"Fechamento: {agora.strftime('%d/%m/%Y às %H:%M')}")
        )
        info_layout.addWidget(
            QLabel(f"Tempo de expediente: {horas:02d}h {minutos:02d}min")
        )

        esperado_titulo = QLabel("Saldo esperado")
        esperado_titulo.setObjectName("cardTitle")

        esperado_valor = QLabel(formatar_moeda(self.valor_esperado))
        esperado_valor.setObjectName("metricValue")

        contado_titulo = QLabel("Valor contado pelo operador")

        self.valor_contado_input = QDoubleSpinBox()
        self.valor_contado_input.setRange(0, 999999999.99)
        self.valor_contado_input.setDecimals(2)
        self.valor_contado_input.setPrefix("R$ ")
        self.valor_contado_input.setMinimumHeight(50)
        self.valor_contado_input.valueChanged.connect(
            self.atualizar_diferenca
        )

        diferenca_titulo = QLabel("Diferença")

        self.diferenca_label = QLabel("R$ 0,00")
        self.diferenca_label.setObjectName("metricValue")

        self.status_label = QLabel(
            "Informe o valor contado para realizar a conferência."
        )
        self.status_label.setWordWrap(True)
        self.status_label.setObjectName("secondaryText")

        justificativa_titulo = QLabel(
            "Justificativa da diferença"
        )

        self.justificativa_input = QLineEdit()
        self.justificativa_input.setPlaceholderText(
            "Obrigatória quando houver sobra ou falta"
        )

        botoes = QHBoxLayout()

        cancelar_button = QPushButton("Cancelar")
        cancelar_button.setObjectName("ghostButton")
        cancelar_button.clicked.connect(self.reject)

        finalizar_button = QPushButton("Finalizar Caixa")
        finalizar_button.setObjectName("primaryButton")
        finalizar_button.clicked.connect(self.finalizar)

        botoes.addWidget(cancelar_button)
        botoes.addWidget(finalizar_button)

        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addWidget(informacoes)
        layout.addWidget(esperado_titulo)
        layout.addWidget(esperado_valor)
        layout.addWidget(contado_titulo)
        layout.addWidget(self.valor_contado_input)
        layout.addWidget(diferenca_titulo)
        layout.addWidget(self.diferenca_label)
        layout.addWidget(self.status_label)
        layout.addWidget(justificativa_titulo)
        layout.addWidget(self.justificativa_input)
        layout.addLayout(botoes)

        self.atualizar_diferenca()

    def atualizar_diferenca(self) -> None:
        contado = self.valor_contado_input.value()
        diferenca = contado - self.valor_esperado

        self.diferenca_label.setText(
            formatar_moeda(diferenca)
        )

        if abs(diferenca) < 0.01:
            self.status_label.setText(
                "✓ Caixa conferido. Nenhuma diferença encontrada."
            )
            self.status_label.setStyleSheet(
                "color: #4ADE80; background: transparent;"
            )
            return

        if diferenca > 0:
            mensagem = (
                f"Foi encontrada uma sobra de "
                f"{formatar_moeda(diferenca)}."
            )
        else:
            mensagem = (
                f"Foi encontrada uma falta de "
                f"{formatar_moeda(abs(diferenca))}."
            )

        self.status_label.setText(mensagem)
        self.status_label.setStyleSheet(
            "color: #FBBF24; background: transparent;"
        )

    def finalizar(self) -> None:
        contado = self.valor_contado_input.value()
        diferenca = contado - self.valor_esperado
        justificativa = self.justificativa_input.text().strip()

        if abs(diferenca) >= 0.01 and not justificativa:
            QMessageBox.warning(
                self,
                "Justificativa obrigatória",
                "Informe uma justificativa para a diferença encontrada.",
            )
            self.justificativa_input.setFocus()
            return

        resposta = QMessageBox.question(
            self,
            "Confirmar fechamento",
            (
                f"Saldo esperado: {formatar_moeda(self.valor_esperado)}\n"
                f"Valor contado: {formatar_moeda(contado)}\n"
                f"Diferença: {formatar_moeda(diferenca)}\n\n"
                "Deseja finalizar o caixa?"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if resposta != QMessageBox.Yes:
            return

        try:
            resultado = caixa_controller.fechar_caixa(
                valor_contado=contado,
                justificativa=justificativa,
            )

            QMessageBox.information(
                self,
                "Caixa encerrado",
                (
                    "Caixa fechado com sucesso.\n\n"
                    f"Saldo esperado: "
                    f"{formatar_moeda(resultado['esperado'])}\n"
                    f"Valor contado: "
                    f"{formatar_moeda(resultado['contado'])}\n"
                    f"Diferença: "
                    f"{formatar_moeda(resultado['diferenca'])}"
                ),
            )

            self.accept()

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Não foi possível fechar",
                str(error),
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Erro no fechamento",
                f"Ocorreu um problema inesperado:\n{error}",
            )
            