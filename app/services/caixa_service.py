from app.database.database import database
from app.services.session_service import session_service
from app.services.pin_service import pin_service


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
            raise ValueError(
                "Já existe um caixa aberto."
            )

        if valor_inicial < 0:
            raise ValueError(
                "O valor inicial não pode ser negativo."
            )

        usuario = session_service.obter_usuario_atual()

        if usuario is None:
            raise ValueError(
                "Nenhum usuário está autenticado."
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
        forma_pagamento: str | None = None,
    ) -> int:
        caixa = database.obter_caixa_aberto()

        if caixa is None:
            raise ValueError(
                "Abra o caixa antes de registrar movimentações."
            )

        tipo_normalizado = (
            tipo.strip().upper()
        )

        if (
            tipo_normalizado
            not in self.TIPOS_PERMITIDOS
        ):
            raise ValueError(
                "Tipo de movimentação inválido."
            )

        if valor <= 0:
            raise ValueError(
                "O valor deve ser maior que zero."
            )

        forma_normalizada = None

        if tipo_normalizado == "VENDA":
            if not forma_pagamento:
                raise ValueError(
                    "Informe a forma de pagamento da venda."
                )

            forma_normalizada = (
                forma_pagamento
                .strip()
                .upper()
            )

            formas_permitidas = {
                "DINHEIRO",
                "PIX",
                "DEBITO",
                "CREDITO",
            }

            if (
                forma_normalizada
                not in formas_permitidas
            ):
                raise ValueError(
                    "Forma de pagamento inválida."
                )

        return database.registrar_movimentacao(
            caixa_id=int(caixa["id"]),
            tipo=tipo_normalizado,
            valor=valor,
            descricao=descricao,
            forma_pagamento=forma_normalizada,
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
                "vendas_dinheiro": 0.0,
                "vendas_pix": 0.0,
                "vendas_debito": 0.0,
                "vendas_credito": 0.0,
                "suprimentos": 0.0,
                "sangrias": 0.0,
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

        esperado = float(
            resumo["saldo_esperado"]
        )

        diferenca = (
            valor_contado - esperado
        )

        if (
            abs(diferenca) >= 0.01
            and not justificativa.strip()
        ):
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

    def listar_caixas_fechados(
        self,
        limite: int = 50,
    ) -> list:
        return database.listar_caixas_fechados(
            limite=limite
        )

    def obter_detalhes_caixa(
        self,
        caixa_id: int,
    ) -> dict:
        detalhes = database.obter_detalhes_caixa(
            caixa_id
        )

        if detalhes is None:
            raise ValueError(
                "Caixa não encontrado."
            )

        return detalhes
    
    def obter_configuracoes_estabelecimento(
        self,
    ) -> dict:
        return {
            "nome": database.obter_configuracao(
                "estabelecimento_nome",
                "Meu Estabelecimento",
            ),
            "responsavel": database.obter_configuracao(
                "responsavel_nome",
                "",
            ),
            "email_relatorios": database.obter_configuracao(
                "email_relatorios",
                "",
            ),
            "enviar_relatorio": (
                database.obter_configuracao(
                    "enviar_relatorio_automaticamente",
                    "0",
                )
                == "1"
            ),
        }


    def salvar_configuracoes_estabelecimento(
        self,
        nome: str,
        responsavel: str,
        email_relatorios: str,
        enviar_relatorio: bool,
    ) -> None:
        nome = nome.strip()
        responsavel = responsavel.strip()
        email_relatorios = email_relatorios.strip()

        if not nome:
            raise ValueError(
                "Informe o nome do estabelecimento."
            )

        database.salvar_configuracao(
            "estabelecimento_nome",
            nome,
        )

        database.salvar_configuracao(
            "responsavel_nome",
            responsavel,
        )

        database.salvar_configuracao(
            "email_relatorios",
            email_relatorios,
        )

        database.salvar_configuracao(
            "enviar_relatorio_automaticamente",
            "1" if enviar_relatorio else "0",
        )


    def autenticar_usuario(
        self,
        usuario: str,
        pin: str,
    ) -> dict:
        usuario = usuario.strip().lower()
        pin = pin.strip()

        if not usuario:
            raise ValueError(
                "Informe o usuário."
            )

        if not pin:
            raise ValueError(
                "Informe o PIN."
            )

        registro = database.obter_usuario_por_login(
            usuario
        )

        if registro is None:
            raise ValueError(
                "Usuário não encontrado ou inativo."
            )

        pin_salvo = str(
            registro["pin_hash"]
        )

        # Migração automática:
        # se ainda estiver em texto puro, valida uma vez
        # e já converte para hash.
        if not pin_service.eh_hash(
            pin_salvo
        ):
            if pin_salvo != pin:
                raise ValueError(
                    "PIN incorreto."
                )

            novo_hash = pin_service.gerar_hash(
                pin
            )

            database.atualizar_pin_usuario(
                usuario_id=int(registro["id"]),
                pin_hash=novo_hash,
            )

        else:
            if not pin_service.verificar_pin(
                pin,
                pin_salvo,
            ):
                raise ValueError(
                    "PIN incorreto."
                )

        session_service.iniciar_sessao(
            registro
        )

        return session_service.obter_usuario_atual()


    def obter_usuario_logado(
        self,
    ) -> dict | None:
        return session_service.obter_usuario_atual()


    def logout(
        self,
    ) -> None:
        session_service.encerrar_sessao()

    def listar_usuarios(
        self,
    ) -> list:
        usuario_atual = (
            session_service.obter_usuario_atual()
        )

        if usuario_atual is None:
            raise ValueError(
                "Nenhum usuário está autenticado."
            )

        if (
            str(
                usuario_atual.get(
                    "perfil",
                    ""
                )
            ).upper()
            != "GERENTE"
        ):
            raise ValueError(
                "Apenas gerentes podem "
                "consultar usuários."
            )

        return database.listar_usuarios()


    def criar_usuario(
        self,
        nome: str,
        usuario: str,
        pin: str,
        perfil: str = "OPERADOR",
    ) -> int:
        usuario_atual = (
            session_service.obter_usuario_atual()
        )

        if usuario_atual is None:
            raise ValueError(
                "Nenhum usuário está autenticado."
            )

        if (
            str(
                usuario_atual.get(
                    "perfil",
                    ""
                )
            ).upper()
            != "GERENTE"
        ):
            raise ValueError(
                "Apenas gerentes podem "
                "cadastrar usuários."
            )

        nome = nome.strip()
        usuario = usuario.strip().lower()
        pin = pin.strip()
        perfil = perfil.strip().upper()

        if not nome:
            raise ValueError(
                "Informe o nome do usuário."
            )

        if not usuario:
            raise ValueError(
                "Informe o login do usuário."
            )

        if len(pin) != 4 or not pin.isdigit():
            raise ValueError(
                "O PIN deve possuir "
                "exatamente 4 números."
            )

        if perfil not in {
            "GERENTE",
            "OPERADOR",
        }:
            raise ValueError(
                "Perfil de usuário inválido."
            )

        existente = (
            database.obter_usuario_por_login(
                usuario
            )
        )

        if existente is not None:
            raise ValueError(
                "Já existe um usuário "
                "com esse login."
            )

        pin_hash = pin_service.gerar_hash(
            pin
        )

        return database.criar_usuario(
            nome=nome,
            usuario=usuario,
            pin_hash=pin_hash,
            perfil=perfil,
        )


    def atualizar_usuario(
        self,
        usuario_id: int,
        nome: str,
        usuario: str,
        perfil: str,
    ) -> None:
        usuario_atual = (
            session_service.obter_usuario_atual()
        )

        if usuario_atual is None:
            raise ValueError(
                "Nenhum usuário está autenticado."
            )

        if (
            str(
                usuario_atual.get(
                    "perfil",
                    ""
                )
            ).upper()
            != "GERENTE"
        ):
            raise ValueError(
                "Apenas gerentes podem "
                "editar usuários."
            )

        nome = nome.strip()
        usuario = usuario.strip().lower()
        perfil = perfil.strip().upper()

        if not nome:
            raise ValueError(
                "Informe o nome do usuário."
            )

        if not usuario:
            raise ValueError(
                "Informe o login do usuário."
            )

        if perfil not in {
            "GERENTE",
            "OPERADOR",
        }:
            raise ValueError(
                "Perfil de usuário inválido."
            )

        database.atualizar_usuario(
            usuario_id=usuario_id,
            nome=nome,
            usuario=usuario,
            perfil=perfil,
        )


    def atualizar_pin_usuario(
        self,
        usuario_id: int,
        novo_pin: str,
    ) -> None:
        usuario_atual = (
            session_service.obter_usuario_atual()
        )

        if usuario_atual is None:
            raise ValueError(
                "Nenhum usuário está autenticado."
            )

        if (
            str(
                usuario_atual.get(
                    "perfil",
                    ""
                )
            ).upper()
            != "GERENTE"
        ):
            raise ValueError(
                "Apenas gerentes podem "
                "alterar PINs."
            )

        novo_pin = novo_pin.strip()

        if (
            len(novo_pin) != 4
            or not novo_pin.isdigit()
        ):
            raise ValueError(
                "O PIN deve possuir "
                "exatamente 4 números."
            )

        novo_hash = pin_service.gerar_hash(
            novo_pin
        )

        database.atualizar_pin_usuario(
            usuario_id=usuario_id,
            pin_hash=novo_hash,
        )


    def alterar_status_usuario(
        self,
        usuario_id: int,
        ativo: bool,
    ) -> None:
        usuario_atual = (
            session_service.obter_usuario_atual()
        )

        if usuario_atual is None:
            raise ValueError(
                "Nenhum usuário está autenticado."
            )

        if (
            str(
                usuario_atual.get(
                    "perfil",
                    ""
                )
            ).upper()
            != "GERENTE"
        ):
            raise ValueError(
                "Apenas gerentes podem "
                "ativar ou desativar usuários."
            )

        if int(usuario_atual["id"]) == usuario_id:
            raise ValueError(
                "Você não pode desativar "
                "o próprio usuário."
            )

        database.alterar_status_usuario(
            usuario_id=usuario_id,
            ativo=ativo,
        )

caixa_service = CaixaService()