from __future__ import annotations

import os
import sys
from pathlib import Path


APP_NAME = "CaixaGo"


def esta_empacotado() -> bool:
    return bool(
        getattr(
            sys,
            "frozen",
            False,
        )
    )


def obter_raiz_projeto() -> Path:
    return (
        Path(__file__)
        .resolve()
        .parents[2]
    )


def obter_diretorio_dados_app() -> Path:
    if esta_empacotado():
        local_app_data = os.getenv(
            "LOCALAPPDATA"
        )

        if not local_app_data:
            raise RuntimeError(
                "LOCALAPPDATA não foi encontrado."
            )

        raiz = (
            Path(local_app_data)
            / APP_NAME
        )

    else:
        raiz = obter_raiz_projeto()

    raiz.mkdir(
        parents=True,
        exist_ok=True,
    )

    return raiz


def obter_diretorio_banco() -> Path:
    caminho = (
        obter_diretorio_dados_app()
        / "data"
    )

    caminho.mkdir(
        parents=True,
        exist_ok=True,
    )

    return caminho


def obter_caminho_banco() -> Path:
    return (
        obter_diretorio_banco()
        / "caixago.db"
    )


def obter_diretorio_backups() -> Path:
    caminho = (
        obter_diretorio_dados_app()
        / "backups"
    )

    caminho.mkdir(
        parents=True,
        exist_ok=True,
    )

    return caminho


def obter_diretorio_relatorios() -> Path:
    caminho = (
        obter_diretorio_dados_app()
        / "relatorios"
    )

    caminho.mkdir(
        parents=True,
        exist_ok=True,
    )

    return caminho