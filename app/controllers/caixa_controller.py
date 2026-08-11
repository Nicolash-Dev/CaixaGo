from app.services.caixa_service import caixa_service


class CaixaController:
    def abrir_caixa(
        self,
        valor: float,
        observacao: str,
    ):
        return caixa_service.abrir_caixa(
            valor_inicial=valor,
            observacao=observacao,
        )

    def obter_caixa_aberto(self):
        return caixa_service.obter_caixa_aberto()

    def registrar_movimentacao(
        self,
        tipo: str,
        valor: float,
        descricao: str = "",
        forma_pagamento: str | None = None,
    ):
        return caixa_service.registrar_movimentacao(
            tipo=tipo,
            valor=valor,
            descricao=descricao,
            forma_pagamento=forma_pagamento,
        )

    def listar_movimentacoes(self):
        return caixa_service.listar_movimentacoes()

    def obter_resumo(self) -> dict:
        return caixa_service.obter_resumo()

    def fechar_caixa(
        self,
        valor_contado: float,
        justificativa: str = "",
    ) -> dict:
        return caixa_service.fechar_caixa(
            valor_contado=valor_contado,
            justificativa=justificativa,
        )

    def obter_ultimas_movimentacoes(
        self,
        limite: int = 5,
    ):
        return caixa_service.obter_ultimas_movimentacoes(
            limite=limite
    )


caixa_controller = CaixaController()