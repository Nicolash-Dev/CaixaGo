from app.database.database import database


class CaixaService:
    TIPOS_PERMITIDOS = {
        "VENDA",
        "SANGRIA",
        "SUPRIMENTO",
    }

    def obter_caixa_aberto(self):
        return database.obter_caixa_aberto()

    def abrir_caixa(
        self,
        valor_inicial: float,
        observacao: str = "",
    ) -> int:
        if database.obter_caixa_aberto() is not None:
            raise ValueError("Já existe um caixa aberto.")

        if valor_inicial < 0:
            raise ValueError(
            "O valor inicial não pode ser negativo."
        )

        usuario = database.obter_usuario_por_login(
        "nicolas"
        )

        if usuario is None:
            raise ValueError(
                "Usuário padrão não foi encontrado."
            )

        return database.abrir_caixa(
        usuario_id=int(usuario["id"]),
        valor_inicial=valor_inicial,
        observacao=observacao.strip(),
    )

    def registrar_movimentacao(
        self,
        tipo: str,
        valor: float,
        descricao: str = "",
    ) -> int:
        caixa = database.obter_caixa_aberto()

        if caixa is None:
            raise ValueError(
                "Abra o caixa antes de registrar movimentações."
            )

        tipo_normalizado = tipo.strip().upper()

        if tipo_normalizado not in self.TIPOS_PERMITIDOS:
            raise ValueError(
                "Tipo de movimentação inválido."
            )

        if valor <= 0:
            raise ValueError(
                "O valor deve ser maior que zero."
            )

        return database.registrar_movimentacao(
            caixa_id=int(caixa["id"]),
            tipo=tipo_normalizado,
            valor=valor,
            descricao=descricao,
        )

    def listar_movimentacoes(self):
        caixa = database.obter_caixa_aberto()

        if caixa is None:
            return []

        return database.listar_movimentacoes(
            int(caixa["id"])
        )

    def obter_ultimas_movimentacoes(
        self,
        limite: int = 5,
    ):
        caixa = database.obter_caixa_aberto()

        if caixa is None:
            return []

        return database.obter_ultimas_movimentacoes(
            caixa_id=int(caixa["id"]),
            limite=limite,
        )

    
    def obter_resumo(self) -> dict:
        caixa = database.obter_caixa_aberto()

        if caixa is None:
            return {
                "quantidade": 0,
                "faturamento": 0.0,
                "saldo_esperado": 0.0,
            }

        return database.calcular_resumo_caixa(
            int(caixa["id"])
        )

    def fechar_caixa(
        self,
        valor_contado: float,
        justificativa: str = "",
    ) -> dict:
        caixa = database.obter_caixa_aberto()

        if caixa is None:
            raise ValueError(
                "Não existe um caixa aberto."
            )

        if valor_contado < 0:
            raise ValueError(
                "O valor contado não pode ser negativo."
            )

        resumo = database.calcular_resumo_caixa(
            int(caixa["id"])
        )

        esperado = float(resumo["saldo_esperado"])
        diferenca = valor_contado - esperado

        if abs(diferenca) >= 0.01 and not justificativa.strip():
            raise ValueError(
                "Informe uma justificativa para a diferença."
            )

        database.fechar_caixa(
            caixa_id=int(caixa["id"]),
            valor_contado=valor_contado,
            diferenca=diferenca,
            observacao=justificativa,
        )

        return {
            "esperado": esperado,
            "contado": valor_contado,
            "diferenca": diferenca,
        }


caixa_service = CaixaService()