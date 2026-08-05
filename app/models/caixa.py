from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Caixa:
    id: Optional[int]
    usuario_id: int
    valor_inicial: float
    status: str
    aberto_em: datetime
    fechado_em: Optional[datetime] = None
    observacao: str = ""

    @property
    def aberto(self) -> bool:
        return self.status == "ABERTO"

    @property
    def fechado(self) -> bool:
        return self.status == "FECHADO"