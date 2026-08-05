from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class Database:
    def __init__(self) -> None:
        project_root = Path(__file__).resolve().parents[2]
        data_directory = project_root / "data"
        data_directory.mkdir(parents=True, exist_ok=True)

        self.database_path = data_directory / "caixago.db"

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")

        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    usuario TEXT NOT NULL UNIQUE,
                    pin_hash TEXT NOT NULL,
                    ativo INTEGER NOT NULL DEFAULT 1,
                    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS caixas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    valor_inicial REAL NOT NULL DEFAULT 0,
                    observacao TEXT,
                    status TEXT NOT NULL DEFAULT 'ABERTO',
                    aberto_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    fechado_em TEXT,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                );

                CREATE TABLE IF NOT EXISTS movimentacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    caixa_id INTEGER NOT NULL,
                    tipo TEXT NOT NULL,
                    valor REAL NOT NULL,
                    descricao TEXT,
                    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (caixa_id) REFERENCES caixas(id)
                );

                CREATE TABLE IF NOT EXISTS configuracoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chave TEXT NOT NULL UNIQUE,
                    valor TEXT,
                    atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            connection.execute(
                """
                INSERT OR IGNORE INTO usuarios (
                    nome,
                    usuario,
                    pin_hash
                )
                VALUES (?, ?, ?)
                """,
                ("Nicolas", "nicolas", "1234"),
            )

    def obter_caixa_aberto(self) -> sqlite3.Row | None:
        with self.connect() as connection:
            return connection.execute(
                """
                SELECT *
                FROM caixas
                WHERE status = 'ABERTO'
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()

    def abrir_caixa(
        self,
        usuario_id: int,
        valor_inicial: float,
        observacao: str,
    ) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO caixas (
                    usuario_id,
                    valor_inicial,
                    observacao,
                    status
                )
                VALUES (?, ?, ?, 'ABERTO')
                """,
                (usuario_id, valor_inicial, observacao),
            )
    def registrar_movimentacao(
        self,
        caixa_id: int,
        tipo: str,
        valor: float,
        descricao: str = "",
    ) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO movimentacoes (
                    caixa_id,
                    tipo,
                    valor,
                    descricao
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    caixa_id,
                    tipo.upper(),
                    valor,
                    descricao.strip(),
                ),
            )

            return int(cursor.lastrowid)


    def listar_movimentacoes(self, caixa_id: int):
        with self.connect() as connection:
            return connection.execute(
                """
                SELECT *
                FROM movimentacoes
                WHERE caixa_id = ?
                ORDER BY criado_em DESC, id DESC
                """,
                (caixa_id,),
            ).fetchall()


    def calcular_resumo_caixa(self, caixa_id: int) -> dict:
        with self.connect() as connection:
            caixa = connection.execute(
                """
                SELECT valor_inicial
                FROM caixas
                WHERE id = ?
                """,
                (caixa_id,),
            ).fetchone()

            if caixa is None:
                raise ValueError("Caixa não encontrado.")

            resumo = connection.execute(
                """
                SELECT
                    COUNT(*) AS quantidade,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN tipo IN ('VENDA', 'SUPRIMENTO')
                                    THEN valor
                                WHEN tipo = 'SANGRIA'
                                    THEN -valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS saldo_movimentacoes,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN tipo = 'VENDA'
                                    THEN valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS faturamento
                FROM movimentacoes
                WHERE caixa_id = ?
                """,
                (caixa_id,),
            ).fetchone()

            valor_inicial = float(caixa["valor_inicial"])
            saldo_movimentacoes = float(resumo["saldo_movimentacoes"])

            return {
                "quantidade": int(resumo["quantidade"]),
                "faturamento": float(resumo["faturamento"]),
                "saldo_esperado": valor_inicial + saldo_movimentacoes,
            }


    def fechar_caixa(
        self,
        caixa_id: int,
        valor_contado: float,
        diferenca: float,
        observacao: str,
    ) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                UPDATE caixas
                SET
                    status = 'FECHADO',
                    fechado_em = CURRENT_TIMESTAMP,
                    observacao = CASE
                        WHEN ? = '' THEN observacao
                        ELSE ?
                    END
                WHERE id = ?
                """,
                (
                    observacao.strip(),
                    observacao.strip(),
                    caixa_id,
                ),
            )

            connection.execute(
                """
                INSERT INTO configuracoes (
                    chave,
                    valor,
                    atualizado_em
                )
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(chave)
                DO UPDATE SET
                    valor = excluded.valor,
                    atualizado_em = CURRENT_TIMESTAMP
                """,
                (
                    f"fechamento_{caixa_id}",
                    (
                        f"valor_contado={valor_contado};"
                        f"diferenca={diferenca};"
                        f"observacao={observacao.strip()}"
                    ),
                ),
            )

            
            connection.execute(
    ...
)


database = Database()