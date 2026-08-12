from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class Database:
    def __init__(self) -> None:
        project_root = Path(__file__).resolve().parents[2]

        data_directory = project_root / "data"
        data_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.database_path = (
            data_directory / "caixago.db"
        )

    @contextmanager
    def connect(
        self,
    ) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = sqlite3.Row

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

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
                    criado_em TEXT NOT NULL
                        DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS caixas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    valor_inicial REAL NOT NULL DEFAULT 0,
                    observacao TEXT,
                    status TEXT NOT NULL DEFAULT 'ABERTO',
                    aberto_em TEXT NOT NULL
                        DEFAULT CURRENT_TIMESTAMP,
                    fechado_em TEXT,
                    FOREIGN KEY (
                        usuario_id
                    ) REFERENCES usuarios(id)
                );

                CREATE TABLE IF NOT EXISTS movimentacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    caixa_id INTEGER NOT NULL,
                    tipo TEXT NOT NULL,
                    valor REAL NOT NULL,
                    descricao TEXT,
                    criado_em TEXT NOT NULL
                        DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (
                        caixa_id
                    ) REFERENCES caixas(id)
                );

                CREATE TABLE IF NOT EXISTS configuracoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chave TEXT NOT NULL UNIQUE,
                    valor TEXT,
                    atualizado_em TEXT NOT NULL
                        DEFAULT CURRENT_TIMESTAMP
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
                (
                    "Nicolas",
                    "nicolas",
                    "1234",
                ),
            )

            # Migração para bancos antigos
            colunas = connection.execute(
                """
                PRAGMA table_info(
                    movimentacoes
                )
                """
            ).fetchall()

            nomes_colunas = {
                coluna["name"]
                for coluna in colunas
            }

            if (
                "forma_pagamento"
                not in nomes_colunas
            ):
                connection.execute(
                    """
                    ALTER TABLE movimentacoes
                    ADD COLUMN
                    forma_pagamento TEXT
                    """
                )

    def obter_caixa_aberto(
        self,
    ) -> sqlite3.Row | None:
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

    def obter_usuario_por_login(
        self,
        usuario: str,
    ) -> sqlite3.Row | None:
        with self.connect() as connection:
            return connection.execute(
                """
                SELECT *
                FROM usuarios
                WHERE usuario = ?
                  AND ativo = 1
                LIMIT 1
                """,
                (usuario,),
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
                VALUES (
                    ?,
                    ?,
                    ?,
                    'ABERTO'
                )
                """,
                (
                    usuario_id,
                    valor_inicial,
                    observacao,
                ),
            )

            return int(
                cursor.lastrowid
            )

    def registrar_movimentacao(
        self,
        caixa_id: int,
        tipo: str,
        valor: float,
        descricao: str = "",
        forma_pagamento: str | None = None,
    ) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO movimentacoes (
                    caixa_id,
                    tipo,
                    valor,
                    descricao,
                    forma_pagamento
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    caixa_id,
                    tipo.upper(),
                    valor,
                    descricao.strip(),
                    (
                        forma_pagamento.upper()
                        if forma_pagamento
                        else None
                    ),
                ),
            )

            return int(
                cursor.lastrowid
            )

    def listar_movimentacoes(
        self,
        caixa_id: int,
    ):
        with self.connect() as connection:
            return connection.execute(
                """
                SELECT *
                FROM movimentacoes
                WHERE caixa_id = ?
                ORDER BY
                    criado_em DESC,
                    id DESC
                """,
                (caixa_id,),
            ).fetchall()

    def obter_ultimas_movimentacoes(
        self,
        caixa_id: int,
        limite: int = 5,
    ):
        with self.connect() as connection:
            return connection.execute(
                """
                SELECT
                    id,
                    caixa_id,
                    tipo,
                    valor,
                    descricao,
                    forma_pagamento,
                    criado_em
                FROM movimentacoes
                WHERE caixa_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (
                    caixa_id,
                    limite,
                ),
            ).fetchall()

    def calcular_resumo_caixa(
        self,
        caixa_id: int,
    ) -> dict:
        with self.connect() as connection:
            caixa = connection.execute(
                """
                SELECT
                    valor_inicial
                FROM caixas
                WHERE id = ?
                """,
                (caixa_id,),
            ).fetchone()

            if caixa is None:
                raise ValueError(
                    "Caixa não encontrado."
                )

            resumo = connection.execute(
                """
                SELECT
                    COUNT(*) AS quantidade,

                    COALESCE(
                        SUM(
                            CASE

                                WHEN tipo = 'VENDA'
                                AND (
                                    forma_pagamento = 'DINHEIRO'
                                    OR forma_pagamento IS NULL
                                )
                                THEN valor

                                WHEN tipo = 'SUPRIMENTO'
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
                    ) AS faturamento,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN tipo = 'VENDA'
                                AND (
                                    forma_pagamento = 'DINHEIRO'
                                    OR forma_pagamento IS NULL
                                )
                                THEN valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS vendas_dinheiro,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN tipo = 'VENDA'
                                AND forma_pagamento = 'PIX'
                                THEN valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS vendas_pix,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN tipo = 'VENDA'
                                AND forma_pagamento = 'DEBITO'
                                THEN valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS vendas_debito,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN tipo = 'VENDA'
                                AND forma_pagamento = 'CREDITO'
                                THEN valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS vendas_credito,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN tipo = 'SUPRIMENTO'
                                THEN valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS suprimentos,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN tipo = 'SANGRIA'
                                THEN valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS sangrias

                FROM movimentacoes
                WHERE caixa_id = ?
                """,
                (caixa_id,),
            ).fetchone()

            valor_inicial = float(
                caixa["valor_inicial"]
            )

            saldo_movimentacoes = float(
                resumo["saldo_movimentacoes"]
            )

            return {
                "quantidade": int(
                    resumo["quantidade"]
                ),

                "faturamento": float(
                    resumo["faturamento"]
                ),

                "saldo_esperado":
                    valor_inicial
                    + saldo_movimentacoes,

                "vendas_dinheiro": float(
                    resumo["vendas_dinheiro"]
                ),

                "vendas_pix": float(
                    resumo["vendas_pix"]
                ),

                "vendas_debito": float(
                    resumo["vendas_debito"]
                ),

                "vendas_credito": float(
                    resumo["vendas_credito"]
                ),

                "suprimentos": float(
                    resumo["suprimentos"]
                ),

                "sangrias": float(
                    resumo["sangrias"]
                ),
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

                        WHEN ? = ''
                        THEN observacao

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
                VALUES (
                    ?,
                    ?,
                    CURRENT_TIMESTAMP
                )

                ON CONFLICT(chave)
                DO UPDATE SET

                    valor = excluded.valor,

                    atualizado_em =
                        CURRENT_TIMESTAMP
                """,
                (
                    f"fechamento_{caixa_id}",
                    (
                        f"valor_contado="
                        f"{valor_contado};"

                        f"diferenca="
                        f"{diferenca};"

                        f"observacao="
                        f"{observacao.strip()}"
                    ),
                ),
            )

    def listar_caixas_fechados(
        self,
        limite: int = 50,
    ) -> list[sqlite3.Row]:
        with self.connect() as connection:
            caixas = connection.execute(
                """
                SELECT
                    c.id,

                    c.usuario_id,

                    c.valor_inicial,

                    c.observacao,

                    c.aberto_em,

                    c.fechado_em,

                    u.nome AS operador,

                    COUNT(
                        m.id
                    ) AS quantidade_eventos,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN m.tipo = 'VENDA'
                                THEN m.valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS faturamento,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN m.tipo = 'VENDA'
                                AND COALESCE(
                                    m.forma_pagamento,
                                    'DINHEIRO'
                                ) = 'DINHEIRO'
                                THEN m.valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS vendas_dinheiro,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN m.tipo = 'VENDA'
                                AND
                                    m.forma_pagamento
                                    = 'PIX'
                                THEN m.valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS vendas_pix,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN m.tipo = 'VENDA'
                                AND
                                    m.forma_pagamento
                                    = 'DEBITO'
                                THEN m.valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS vendas_debito,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN m.tipo = 'VENDA'
                                AND
                                    m.forma_pagamento
                                    = 'CREDITO'
                                THEN m.valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS vendas_credito,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN m.tipo = 'SUPRIMENTO'
                                THEN m.valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS suprimentos,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN m.tipo = 'SANGRIA'
                                THEN m.valor
                                ELSE 0
                            END
                        ),
                        0
                    ) AS sangrias

                FROM caixas c

                JOIN usuarios u
                    ON u.id = c.usuario_id

                LEFT JOIN movimentacoes m
                    ON m.caixa_id = c.id

                WHERE
                    c.status = 'FECHADO'

                GROUP BY
                    c.id,
                    c.usuario_id,
                    c.valor_inicial,
                    c.observacao,
                    c.aberto_em,
                    c.fechado_em,
                    u.nome

                ORDER BY
                    c.id DESC

                LIMIT ?
                """,
                (limite,),
            ).fetchall()

            return list(caixas)


    def obter_detalhes_caixa(
        self,
        caixa_id: int,
    ) -> dict | None:
        with self.connect() as connection:
            caixa = connection.execute(
                """
                SELECT
                    c.id,
                    c.usuario_id,
                    c.valor_inicial,
                    c.observacao,
                    c.status,
                    c.aberto_em,
                    c.fechado_em,
                    u.nome AS operador
                FROM caixas c
                JOIN usuarios u
                    ON u.id = c.usuario_id
                WHERE c.id = ?
                LIMIT 1
                """,
                (caixa_id,),
            ).fetchone()

            if caixa is None:
                return None

            movimentacoes = connection.execute(
                """
                SELECT
                    id,
                    tipo,
                    valor,
                    descricao,
                    forma_pagamento,
                    criado_em
                FROM movimentacoes
                WHERE caixa_id = ?
                ORDER BY id ASC
                """,
                (caixa_id,),
            ).fetchall()

        resumo = self.calcular_resumo_caixa(
            caixa_id
        )

        return {
            "caixa": dict(caixa),
            "movimentacoes": [
                dict(movimentacao)
                for movimentacao in movimentacoes
            ],
            "resumo": resumo,
        }

        def salvar_configuracao(
            self,
            chave: str,
            valor: str,
        ) -> None:
            with self.connect() as connection:
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
                    chave,
                    valor,
                ),
            )


    def obter_configuracao(
        self,
        chave: str,
        padrao: str = "",
    ) -> str:
        with self.connect() as connection:
            resultado = connection.execute(
                """
                SELECT valor
                FROM configuracoes
                WHERE chave = ?
                LIMIT 1
                """,
                (chave,),
            ).fetchone()

            if resultado is None:
                return padrao

            return str(
                resultado["valor"]
                or padrao
            )

    def salvar_configuracao(
            self,
            chave: str,
            valor: str,
        ) -> None:
            with self.connect() as connection:
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
                        chave,
                        valor,
                    ),
                )

    def obter_configuracao(
        self,
        chave: str,
        padrao: str = "",
    ) -> str:
        with self.connect() as connection:
            resultado = connection.execute(
                """
                SELECT valor
                FROM configuracoes
                WHERE chave = ?
                LIMIT 1
                """,
                (chave,),
            ).fetchone()

            if resultado is None:
                return padrao

            return str(
                resultado["valor"]
                or padrao
            )

database = Database()