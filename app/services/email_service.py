from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(ENV_PATH)


def formatar_moeda(valor: float) -> str:
    texto = f"{valor:,.2f}"

    texto = (
        texto.replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {texto}"


class EmailService:
    def __init__(self) -> None:
        self.smtp_host = os.getenv(
            "CAIXAGO_SMTP_HOST",
            "",
        ).strip()

        self.smtp_port = int(
            os.getenv(
                "CAIXAGO_SMTP_PORT",
                "587",
            )
        )

        self.smtp_usuario = os.getenv(
            "CAIXAGO_SMTP_USUARIO",
            "",
        ).strip()

        self.smtp_senha = os.getenv(
            "CAIXAGO_SMTP_SENHA",
            "",
        ).strip()

        self.email_remetente = os.getenv(
            "CAIXAGO_EMAIL_REMETENTE",
            self.smtp_usuario,
        ).strip()

        self.usar_tls = (
            os.getenv(
                "CAIXAGO_SMTP_TLS",
                "1",
            )
            == "1"
        )

    def validar_configuracao(self) -> None:
        campos_faltando = []

        if not self.smtp_host:
            campos_faltando.append(
                "CAIXAGO_SMTP_HOST"
            )

        if not self.smtp_usuario:
            campos_faltando.append(
                "CAIXAGO_SMTP_USUARIO"
            )

        if not self.smtp_senha:
            campos_faltando.append(
                "CAIXAGO_SMTP_SENHA"
            )

        if not self.email_remetente:
            campos_faltando.append(
                "CAIXAGO_EMAIL_REMETENTE"
            )

        if campos_faltando:
            raise ValueError(
                "Configuração de e-mail incompleta: "
                + ", ".join(campos_faltando)
            )

    def enviar_relatorio_fechamento(
        self,
        destinatario: str,
        arquivo_pdf: str | Path,
        caixa_id: int,
        estabelecimento: str = "CaixaGo",
        faturamento: float | None = None,
        diferenca: float | None = None,
    ) -> None:
        self.validar_configuracao()

        destinatario = destinatario.strip()
        estabelecimento = estabelecimento.strip()

        if not destinatario:
            raise ValueError(
                "Informe o e-mail do responsável."
            )

        if not estabelecimento:
            estabelecimento = "CaixaGo"

        arquivo_pdf = Path(
            arquivo_pdf
        )

        if not arquivo_pdf.exists():
            raise FileNotFoundError(
                f"PDF não encontrado: {arquivo_pdf}"
            )

        mensagem = EmailMessage()

        mensagem["From"] = (
            self.email_remetente
        )

        mensagem["To"] = (
            destinatario
        )

        mensagem["Subject"] = (
            f"CaixaGo - Fechamento do Caixa #{caixa_id}"
        )

        linhas = [
            "Olá,",
            "",
            (
                f"O fechamento do Caixa #{caixa_id} "
                f"do estabelecimento {estabelecimento} "
                "foi concluído com sucesso."
            ),
        ]

        if faturamento is not None:
            linhas.extend(
                [
                    "",
                    (
                        "Faturamento do expediente: "
                        f"{formatar_moeda(faturamento)}"
                    ),
                ]
            )

        if diferenca is not None:
            linhas.append(
                (
                    "Diferença encontrada: "
                    f"{formatar_moeda(diferenca)}"
                )
            )

        linhas.extend(
            [
                "",
                "O relatório completo está anexado a este e-mail.",
                "",
                "CaixaGo",
                "Conte o dinheiro. O resto é com a gente.",
            ]
        )

        mensagem.set_content(
            "\n".join(linhas)
        )

        with arquivo_pdf.open(
            "rb"
        ) as arquivo:
            mensagem.add_attachment(
                arquivo.read(),
                maintype="application",
                subtype="pdf",
                filename=arquivo_pdf.name,
            )

        with smtplib.SMTP(
            self.smtp_host,
            self.smtp_port,
            timeout=30,
        ) as servidor:

            if self.usar_tls:
                servidor.starttls()

            servidor.login(
                self.smtp_usuario,
                self.smtp_senha,
            )

            servidor.send_message(
                mensagem
            )


email_service = EmailService()