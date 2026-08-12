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

    def listar_caixas_fechados(
        self,
        limite: int = 50,
    ) -> list:
        return caixa_service.listar_caixas_fechados(
            limite=limite
        )

    def obter_detalhes_caixa(
        self,
        caixa_id: int,
    ) -> dict:
        return caixa_service.obter_detalhes_caixa(
            caixa_id
        )

    def obter_configuracoes_estabelecimento(
        self,
    ) -> dict:
        return (
            caixa_service
            .obter_configuracoes_estabelecimento()
        )


    def salvar_configuracoes_estabelecimento(
        self,
        nome: str,
        responsavel: str,
        email_relatorios: str,
        enviar_relatorio: bool,
    ) -> None:
        caixa_service.salvar_configuracoes_estabelecimento(
            nome=nome,
            responsavel=responsavel,
            email_relatorios=email_relatorios,
            enviar_relatorio=enviar_relatorio,
        )

    def autenticar_usuario(
        self,
        usuario: str,
        pin: str,
    ) -> dict:
        return caixa_service.autenticar_usuario(
            usuario=usuario,
            pin=pin,
        )


    def obter_usuario_logado(
        self,
    ) -> dict | None:
        return caixa_service.obter_usuario_logado()


    def logout(
        self,
    ) -> None:
        caixa_service.logout()


    
caixa_controller = CaixaController()