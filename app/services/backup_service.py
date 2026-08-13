from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from app.database.database import database
from app.utils.paths import obter_diretorio_backups


class BackupService:
    LIMITE_BACKUPS = 30

    def __init__(self) -> None:
        self.backup_directory = (
            obter_diretorio_backups()
        )

    def criar_backup(self) -> Path:
        banco_origem = (
            database.database_path
        )

        if not banco_origem.exists():
            raise FileNotFoundError(
                "Banco de dados do CaixaGo "
                "não foi encontrado."
            )

        agora = datetime.now()

        nome_arquivo = (
            "caixago_"
            + agora.strftime(
                "%Y-%m-%d_%H-%M-%S"
            )
            + ".db"
        )

        destino = (
            self.backup_directory
            / nome_arquivo
        )

        shutil.copy2(
            banco_origem,
            destino,
        )

        self.limpar_backups_antigos()

        return destino

    def listar_backups(
        self,
    ) -> list[Path]:
        backups = list(
            self.backup_directory.glob(
                "caixago_*.db"
            )
        )

        backups.sort(
            key=lambda arquivo:
                arquivo.stat().st_mtime,
            reverse=True,
        )

        return backups

    def limpar_backups_antigos(
        self,
    ) -> None:
        backups = self.listar_backups()

        for backup in backups[
            self.LIMITE_BACKUPS:
        ]:
            try:
                backup.unlink()

            except OSError:
                pass

    def restaurar_backup(
        self,
        caminho_backup: str | Path,
    ) -> None:
        caminho_backup = Path(
            caminho_backup
        )

        if not caminho_backup.exists():
            raise FileNotFoundError(
                "O arquivo de backup "
                "não foi encontrado."
            )

        if (
            caminho_backup.suffix.lower()
            != ".db"
        ):
            raise ValueError(
                "O arquivo selecionado "
                "não é um backup válido."
            )

        banco_destino = (
            database.database_path
        )

        # Antes de restaurar, salva o estado
        # atual para permitir recuperação.
        self.criar_backup()

        shutil.copy2(
            caminho_backup,
            banco_destino,
        )

    def obter_backup_mais_recente(
        self,
    ) -> Path | None:
        backups = (
            self.listar_backups()
        )

        if not backups:
            return None

        return backups[0]


backup_service = BackupService()