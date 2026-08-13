from datetime import datetime, timezone

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.controllers.caixa_controller import caixa_controller
from app.reports.fechamento_pdf import gerar_pdf_fechamento
from app.services.email_service import email_service
from app.services.backup_service import backup_service


def formatar_moeda(valor: float) -> str:
    texto = f"{valor:,.2f}"
    texto = (
        texto.replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
    return f"R$ {texto}"


def converter_data_sqlite_para_local(
    data_sqlite: str,
) -> datetime:
    data_utc = datetime.fromisoformat(data_sqlite)

    if data_utc.tzinfo is None:
        data_utc = data_utc.replace(
            tzinfo=timezone.utc
        )

    return data_utc.astimezone()


class FecharCaixaDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Fechar Caixa")
        self.setModal(True)
        self.setMinimumWidth(620)

        caixa = caixa_controller.obter_caixa_aberto()

        if caixa is None:
            raise ValueError(
                "Não existe um caixa aberto."
            )

        self.caixa_id = int(caixa["id"])

        self.resumo = caixa_controller.obter_resumo()

        self.valor_esperado = float(
            self.resumo["saldo_esperado"]
        )

        self.faturamento = float(
            self.resumo["faturamento"]
        )

        self.vendas_dinheiro = float(
            self.resumo["vendas_dinheiro"]
        )

        self.vendas_pix = float(
            self.resumo["vendas_pix"]
        )

        self.vendas_debito = float(
            self.resumo["vendas_debito"]
        )

        self.vendas_credito = float(
            self.resumo["vendas_credito"]
        )

        aberto_em = converter_data_sqlite_para_local(
            str(caixa["aberto_em"])
        )

        agora = datetime.now().astimezone()

        duracao = agora - aberto_em

        segundos = max(
            0,
            int(duracao.total_seconds()),
        )

        horas, restante = divmod(
            segundos,
            3600,
        )

        minutos, _ = divmod(
            restante,
            60,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            32,
            30,
            32,
            30,
        )
        layout.setSpacing(18)

        titulo = QLabel(
            "Fechamento de Caixa"
        )
        titulo.setObjectName("pageTitle")

        subtitulo = QLabel(
            "Confira os valores antes de encerrar o expediente."
        )
        subtitulo.setObjectName("secondaryText")

        # Informações do expediente
        informacoes = QFrame()
        informacoes.setObjectName("goCard")

        info_layout = QVBoxLayout(
            informacoes
        )
        info_layout.setContentsMargins(
            22,
            18,
            22,
            18,
        )
        info_layout.setSpacing(8)

        info_layout.addWidget(
            QLabel(
                "Abertura: "
                f"{aberto_em.strftime('%d/%m/%Y às %H:%M')}"
            )
        )

        info_layout.addWidget(
            QLabel(
                "Fechamento: "
                f"{agora.strftime('%d/%m/%Y às %H:%M')}"
            )
        )

        info_layout.addWidget(
            QLabel(
                "Tempo de expediente: "
                f"{horas:02d}h "
                f"{minutos:02d}min"
            )
        )

        # Resumo das vendas
        vendas_card = QFrame()
        vendas_card.setObjectName("goCard")

        vendas_layout = QGridLayout(
            vendas_card
        )
        vendas_layout.setContentsMargins(
            22,
            18,
            22,
            18,
        )
        vendas_layout.setHorizontalSpacing(20)
        vendas_layout.setVerticalSpacing(10)

        vendas_titulo = QLabel(
            "Resumo das vendas"
        )
        vendas_titulo.setObjectName(
            "sectionTitle"
        )

        vendas_layout.addWidget(
            vendas_titulo,
            0,
            0,
            1,
            2,
        )

        self.adicionar_linha_resumo(
            vendas_layout,
            1,
            "Dinheiro",
            self.vendas_dinheiro,
        )

        self.adicionar_linha_resumo(
            vendas_layout,
            2,
            "PIX",
            self.vendas_pix,
        )

        self.adicionar_linha_resumo(
            vendas_layout,
            3,
            "Débito",
            self.vendas_debito,
        )

        self.adicionar_linha_resumo(
            vendas_layout,
            4,
            "Crédito",
            self.vendas_credito,
        )

        total_label = QLabel(
            "Total"
        )
        total_label.setObjectName(
            "cardTitle"
        )

        total_valor = QLabel(
            formatar_moeda(
                self.faturamento
            )
        )
        total_valor.setObjectName(
            "metricValue"
        )
        total_valor.setAlignment(
            Qt.AlignRight
        )

        vendas_layout.addWidget(
            total_label,
            5,
            0,
        )

        vendas_layout.addWidget(
            total_valor,
            5,
            1,
        )

        # Conferência
        conferencia_titulo = QLabel(
            "Conferência do caixa"
        )
        conferencia_titulo.setObjectName(
            "sectionTitle"
        )

        esperado_titulo = QLabel(
            "Saldo esperado em dinheiro"
        )
        esperado_titulo.setObjectName(
            "cardTitle"
        )

        esperado_valor = QLabel(
            formatar_moeda(
                self.valor_esperado
            )
        )
        esperado_valor.setObjectName(
            "metricValue"
        )

        contado_titulo = QLabel(
            "Valor contado pelo operador"
        )

        self.valor_contado_input = (
            QDoubleSpinBox()
        )
        self.valor_contado_input.setRange(
            0,
            999999999.99,
        )
        self.valor_contado_input.setDecimals(
            2
        )
        self.valor_contado_input.setPrefix(
            "R$ "
        )
        self.valor_contado_input.setMinimumHeight(
            50
        )
        self.valor_contado_input.valueChanged.connect(
            self.atualizar_diferenca
        )

        diferenca_titulo = QLabel(
            "Diferença"
        )

        self.diferenca_label = QLabel(
            "R$ 0,00"
        )
        self.diferenca_label.setObjectName(
            "metricValue"
        )

        self.status_label = QLabel(
            "Informe o valor contado para realizar a conferência."
        )
        self.status_label.setWordWrap(True)
        self.status_label.setObjectName(
            "secondaryText"
        )

        justificativa_titulo = QLabel(
            "Justificativa da diferença"
        )

        self.justificativa_input = (
            QLineEdit()
        )
        self.justificativa_input.setPlaceholderText(
            "Obrigatória quando houver sobra ou falta"
        )

        botoes = QHBoxLayout()

        cancelar_button = QPushButton(
            "Cancelar"
        )
        cancelar_button.setObjectName(
            "ghostButton"
        )
        cancelar_button.clicked.connect(
            self.reject
        )

        finalizar_button = QPushButton(
            "Finalizar Caixa"
        )
        finalizar_button.setObjectName(
            "primaryButton"
        )
        finalizar_button.clicked.connect(
            self.finalizar
        )

        botoes.addWidget(
            cancelar_button
        )
        botoes.addWidget(
            finalizar_button
        )

        layout.addWidget(
            titulo
        )
        layout.addWidget(
            subtitulo
        )
        layout.addWidget(
            informacoes
        )
        layout.addWidget(
            vendas_card
        )
        layout.addWidget(
            conferencia_titulo
        )
        layout.addWidget(
            esperado_titulo
        )
        layout.addWidget(
            esperado_valor
        )
        layout.addWidget(
            contado_titulo
        )
        layout.addWidget(
            self.valor_contado_input
        )
        layout.addWidget(
            diferenca_titulo
        )
        layout.addWidget(
            self.diferenca_label
        )
        layout.addWidget(
            self.status_label
        )
        layout.addWidget(
            justificativa_titulo
        )
        layout.addWidget(
            self.justificativa_input
        )
        layout.addLayout(
            botoes
        )

        self.atualizar_diferenca()

    def adicionar_linha_resumo(
        self,
        layout: QGridLayout,
        linha: int,
        descricao: str,
        valor: float,
    ) -> None:
        descricao_label = QLabel(
            descricao
        )
        descricao_label.setObjectName(
            "secondaryText"
        )

        valor_label = QLabel(
            formatar_moeda(valor)
        )
        valor_label.setAlignment(
            Qt.AlignRight
        )
        valor_label.setStyleSheet(
            """
            color: #F8FAFC;
            background-color: transparent;
            font-weight: 700;
            """
        )

        layout.addWidget(
            descricao_label,
            linha,
            0,
        )

        layout.addWidget(
            valor_label,
            linha,
            1,
        )

    def atualizar_diferenca(
        self,
    ) -> None:
        contado = (
            self.valor_contado_input.value()
        )

        diferenca = (
            contado
            - self.valor_esperado
        )

        # Evita mostrar -0,00
        if abs(diferenca) < 0.005:
            diferenca = 0.0

        self.diferenca_label.setText(
            formatar_moeda(diferenca)
        )

        if abs(diferenca) < 0.01:
            self.status_label.setText(
                "✓ Caixa conferido. "
                "Nenhuma diferença encontrada."
            )

            self.status_label.setStyleSheet(
                "color: #4ADE80; "
                "background: transparent;"
            )
            return

        if diferenca > 0:
            mensagem = (
                "Foi encontrada uma sobra de "
                f"{formatar_moeda(diferenca)}."
            )

        else:
            mensagem = (
                "Foi encontrada uma falta de "
                f"{formatar_moeda(abs(diferenca))}."
            )

        self.status_label.setText(
            mensagem
        )

        self.status_label.setStyleSheet(
            "color: #FBBF24; "
            "background: transparent;"
        )

    def finalizar(self) -> None:
        contado = (
            self.valor_contado_input.value()
        )

        diferenca = (
            contado
            - self.valor_esperado
        )

        if abs(diferenca) < 0.005:
            diferenca = 0.0

        justificativa = (
            self.justificativa_input
            .text()
            .strip()
        )

        if (
            abs(diferenca) >= 0.01
            and not justificativa
        ):
            QMessageBox.warning(
                self,
                "Justificativa obrigatória",
                (
                    "Informe uma justificativa "
                    "para a diferença encontrada."
                ),
            )

            self.justificativa_input.setFocus()
            return

        resposta = QMessageBox.question(
            self,
            "Confirmar fechamento",
            (
                "Resumo das vendas\n\n"
                f"Dinheiro: "
                f"{formatar_moeda(self.vendas_dinheiro)}\n"
                f"PIX: "
                f"{formatar_moeda(self.vendas_pix)}\n"
                f"Débito: "
                f"{formatar_moeda(self.vendas_debito)}\n"
                f"Crédito: "
                f"{formatar_moeda(self.vendas_credito)}\n"
                f"Total: "
                f"{formatar_moeda(self.faturamento)}\n\n"
                "Conferência\n\n"
                f"Saldo esperado: "
                f"{formatar_moeda(self.valor_esperado)}\n"
                f"Valor contado: "
                f"{formatar_moeda(contado)}\n"
                f"Diferença: "
                f"{formatar_moeda(diferenca)}\n\n"
                "Deseja finalizar o caixa?"
            ),
            QMessageBox.Yes
            | QMessageBox.No,
            QMessageBox.No,
        )

        if resposta != QMessageBox.Yes:
            return

        try:
            resultado = (
                caixa_controller
                .fechar_caixa(
                    valor_contado=contado,
                    justificativa=justificativa,
                )
            )

            diferenca_resultado = float(
                resultado["diferenca"]
            )

            if abs(diferenca_resultado) < 0.005:
                diferenca_resultado = 0.0

            caminho_pdf = None
            erro_pdf = None
            email_enviado = False
            erro_email = None
            caminho_backup = None
            erro_backup = None

            try:
                detalhes = (
                    caixa_controller
                    .obter_detalhes_caixa(
                        self.caixa_id
                    )
                )

                caminho_pdf = gerar_pdf_fechamento(
                    detalhes
                )

            except Exception as error:
                erro_pdf = str(error)

            if caminho_pdf is not None:
                try:
                    configuracoes = (
                        caixa_controller
                        .obter_configuracoes_estabelecimento()
                    )

                    enviar_automaticamente = bool(
                        configuracoes.get(
                            "enviar_relatorio",
                            False,
                        )
                    )

                    if enviar_automaticamente:
                        destinatario = str(
                            configuracoes.get(
                                "email_relatorios",
                                "",
                            )
                        ).strip()

                        estabelecimento = str(
                            configuracoes.get(
                                "nome",
                                "CaixaGo",
                            )
                        ).strip()

                        if not destinatario:
                            raise ValueError(
                                "O envio automático está ativado, "
                                "mas nenhum e-mail para relatórios "
                                "foi configurado."
                            )

                        email_service.enviar_relatorio_fechamento(
                            destinatario=destinatario,
                            arquivo_pdf=caminho_pdf,
                            caixa_id=self.caixa_id,
                            estabelecimento=estabelecimento,
                            faturamento=self.faturamento,
                            diferenca=diferenca_resultado,
                        )

                        email_enviado = True

                except Exception as error:
                    erro_email = str(error)

            try:
                caminho_backup = backup_service.criar_backup()

            except Exception as error:
                erro_backup = str(error)

            mensagem = (
                "Caixa fechado com sucesso.\n\n"
                f"Faturamento total: "
                f"{formatar_moeda(self.faturamento)}\n"
                f"Dinheiro: "
                f"{formatar_moeda(self.vendas_dinheiro)}\n"
                f"PIX: "
                f"{formatar_moeda(self.vendas_pix)}\n"
                f"Débito: "
                f"{formatar_moeda(self.vendas_debito)}\n"
                f"Crédito: "
                f"{formatar_moeda(self.vendas_credito)}\n\n"
                f"Saldo esperado: "
                f"{formatar_moeda(resultado['esperado'])}\n"
                f"Valor contado: "
                f"{formatar_moeda(resultado['contado'])}\n"
                f"Diferença: "
                f"{formatar_moeda(diferenca_resultado)}"
            )

            if caminho_pdf is not None:
                mensagem += (
                    "\n\nRelatório PDF gerado automaticamente."
                    f"\n\nArquivo:\n{caminho_pdf}"
                )

            elif erro_pdf:
                mensagem += (
                    "\n\nO caixa foi fechado normalmente,"
                    "\nmas não foi possível gerar o PDF."
                    f"\n\nDetalhes: {erro_pdf}"
                )

            if email_enviado:
                mensagem += (
                    "\n\nRelatório enviado por e-mail "
                    "com sucesso."
                )

            elif erro_email:
                mensagem += (
                    "\n\nO caixa e o PDF foram salvos normalmente,"
                    "\nmas não foi possível enviar o e-mail."
                    f"\n\nDetalhes: {erro_email}"
                )

            if caminho_backup is not None:
                mensagem += (
                    "\n\nBackup automático criado com sucesso."
                    f"\n\nArquivo:\n{caminho_backup}"
                )

            elif erro_backup:
                mensagem += (
                    "\n\nO fechamento foi concluído normalmente,"
                    "\nmas não foi possível criar o backup."
                    f"\n\nDetalhes: {erro_backup}"
                )

            QMessageBox.information(
                self,
                "Caixa encerrado",
                mensagem,
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
                (
                    "Ocorreu um problema inesperado:\n"
                    f"{error}"
                ),
            )