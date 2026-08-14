from __future__ import annotations

import keyring


class CredentialService:
    SERVICE_NAME = "CaixaGo"
    SMTP_KEY = "smtp_password"

    def salvar_senha_smtp(
        self,
        usuario: str,
        senha: str,
    ) -> None:
        usuario = usuario.strip()
        senha = senha.strip()

        if not usuario:
            raise ValueError(
                "Informe o usuário SMTP."
            )

        if not senha:
            raise ValueError(
                "Informe a senha do aplicativo."
            )

        chave = self._criar_chave_usuario(
            usuario
        )

        keyring.set_password(
            self.SERVICE_NAME,
            chave,
            senha,
        )

    def obter_senha_smtp(
        self,
        usuario: str,
    ) -> str | None:
        usuario = usuario.strip()

        if not usuario:
            return None

        chave = self._criar_chave_usuario(
            usuario
        )

        return keyring.get_password(
            self.SERVICE_NAME,
            chave,
        )

    def remover_senha_smtp(
        self,
        usuario: str,
    ) -> None:
        usuario = usuario.strip()

        if not usuario:
            return

        chave = self._criar_chave_usuario(
            usuario
        )

        try:
            keyring.delete_password(
                self.SERVICE_NAME,
                chave,
            )

        except keyring.errors.PasswordDeleteError:
            pass

    def possui_senha_smtp(
        self,
        usuario: str,
    ) -> bool:
        return bool(
            self.obter_senha_smtp(
                usuario
            )
        )

    @staticmethod
    def _criar_chave_usuario(
        usuario: str,
    ) -> str:
        return (
            "smtp:"
            + usuario.strip().lower()
        )


credential_service = CredentialService()