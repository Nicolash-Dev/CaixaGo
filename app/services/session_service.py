class SessionService:
    def __init__(self) -> None:
        self.usuario_atual = None

    def iniciar_sessao(
        self,
        usuario,
    ) -> None:
        self.usuario_atual = {
            "id": int(usuario["id"]),
            "nome": str(usuario["nome"]),
            "usuario": str(usuario["usuario"]),
        }

    def encerrar_sessao(self) -> None:
        self.usuario_atual = None

    def obter_usuario_atual(
        self,
    ) -> dict | None:
        return self.usuario_atual

    def esta_logado(self) -> bool:
        return self.usuario_atual is not None


session_service = SessionService()