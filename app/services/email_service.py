from __future__ import annotations

import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"

# O .env continua disponível para desenvolvimento.
# Na versão empacotada/comercial, as credenciais poderão
# ser carregadas de um armazenamento seguro do Windows.
if not getattr(sys, "frozen", False):
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
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_usuario = ""
        self.smtp_senha = ""
        self.email_remetente = ""
        self.usar_tls = True

        self.carregar_configuracao_ambiente()

    def carregar_configuracao_ambiente(
        self,
    ) -> None:
        """
        Carrega configuração do .env quando disponível.

        Serve para desenvolvimento e mantém compatibilidade
        com o fluxo atual do CaixaGo.
        """
        host = os.getenv(
            "CAIXAGO_SMTP_HOST",
            "",
        ).strip()

        porta_texto = os.getenv(
            "CAIXAGO_SMTP_PORT",
            "",
        ).strip()

        usuario = os.getenv(
            "CAIXAGO_SMTP_USUARIO",
            "",
        ).strip()

        senha = os.getenv(
            "CAIXAGO_SMTP_SENHA",
            "",
        ).strip()

        remetente = os.getenv(
            "CAIXAGO_EMAIL_REMETENTE",
            "",
        ).strip()

        tls_texto = os.getenv(
            "CAIXAGO_SMTP_TLS",
            "",
        ).strip()

        if host:
            self.smtp_host = host

        if porta_texto:
            try:
                self.smtp_port = int(
                    porta_texto
                )
            except ValueError:
                self.smtp_port = 587

        if usuario:
            self.smtp_usuario = usuario

        if senha:
            self.smtp_senha = senha

        if remetente:
            self.email_remetente = remetente

        elif usuario:
            self.email_remetente = usuario

        if tls_texto:
            self.usar_tls = (
                tls_texto == "1"
            )

    def configurar(
        self,
        usuario: str,
        senha: str,
        remetente: str = "",
        host: str = "smtp.gmail.com",
        porta: int = 587,
        usar_tls: bool = True,
    ) -> None:
        """
        Configura o serviço em tempo de execução.

        Esta função será usada pela versão comercial depois
        que as credenciais forem recuperadas do armazenamento
        seguro do Windows.
        """
        usuario = usuario.strip()
        senha = senha.strip()
        remetente = remetente.strip()
        host = host.strip()

        if not usuario:
            raise ValueError(
                "Informe o usuário SMTP."
            )

        if not senha:
            raise ValueError(
                "Informe a senha do aplicativo."
            )

        if not host:
            raise ValueError(
                "Informe o servidor SMTP."
            )

        if porta <= 0:
            raise ValueError(
                "A porta SMTP é inválida."
            )

        self.smtp_host = host
        self.smtp_port = int(porta)
        self.smtp_usuario = usuario
        self.smtp_senha = senha
        self.email_remetente = (
            remetente
            or usuario
        )
        self.usar_tls = bool(
            usar_tls
        )

    def limpar_credenciais(
        self,
    ) -> None:
        """
        Remove apenas as credenciais mantidas em memória.
        """
        self.smtp_usuario = ""
        self.smtp_senha = ""
        self.email_remetente = ""

    def obter_resumo_configuracao(
        self,
    ) -> dict:
        """
        Retorna apenas dados não sensíveis.

        A senha nunca é devolvida.
        """
        return {
            "host": self.smtp_host,
            "porta": self.smtp_port,
            "usuario": self.smtp_usuario,
            "remetente": self.email_remetente,
            "usar_tls": self.usar_tls,
            "possui_senha": bool(
                self.smtp_senha
            ),
        }

    def validar_configuracao(
        self,
    ) -> None:
        campos_faltando = []

        if not self.smtp_host:
            campos_faltando.append(
                "servidor SMTP"
            )

        if not self.smtp_usuario:
            campos_faltando.append(
                "usuário SMTP"
            )

        if not self.smtp_senha:
            campos_faltando.append(
                "senha do aplicativo"
            )

        if not self.email_remetente:
            campos_faltando.append(
                "e-mail remetente"
            )

        if campos_faltando:
            raise ValueError(
                "Configuração de e-mail incompleta: "
                + ", ".join(
                    campos_faltando
                )
            )

    def testar_conexao(
        self,
    ) -> None:
        """
        Testa conexão e autenticação SMTP sem enviar e-mail.
        """
        self.validar_configuracao()

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

    def enviar_email_teste(
        self,
        destinatario: str,
        estabelecimento: str = "CaixaGo",
    ) -> None:
        """
        Envia uma mensagem simples para validar a configuração.
        """
        self.validar_configuracao()

        destinatario = (
            destinatario
            .strip()
        )

        estabelecimento = (
            estabelecimento
            .strip()
        )

        if not destinatario:
            raise ValueError(
                "Informe o e-mail de destino."
            )

        if not estabelecimento:
            estabelecimento = "CaixaGo"

        mensagem = EmailMessage()

        mensagem["From"] = (
            self.email_remetente
        )

        mensagem["To"] = (
            destinatario
        )

        mensagem["Subject"] = (
            "CaixaGo - Teste de e-mail"
        )

        mensagem.set_content(
            (
                "Olá,\n\n"
                "A configuração de e-mail do CaixaGo "
                "está funcionando corretamente.\n\n"
                f"Estabelecimento: {estabelecimento}\n\n"
                "CaixaGo\n"
                "Conte o dinheiro. O resto é com a gente."
            )
        )

        self._enviar_mensagem(
            mensagem
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
            "\n".join(
                linhas
            )
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

        self._enviar_mensagem(
            mensagem
        )

    def _enviar_mensagem(
        self,
        mensagem: EmailMessage,
    ) -> None:
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