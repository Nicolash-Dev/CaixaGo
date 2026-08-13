from __future__ import annotations

import hashlib
import hmac
import secrets


class PinService:
    ITERACOES = 600_000
    PREFIXO = "pbkdf2_sha256"

    def gerar_hash(
        self,
        pin: str,
    ) -> str:
        pin = pin.strip()

        if len(pin) != 4 or not pin.isdigit():
            raise ValueError(
                "O PIN deve possuir exatamente 4 números."
            )

        salt = secrets.token_hex(16)

        hash_bytes = hashlib.pbkdf2_hmac(
            "sha256",
            pin.encode("utf-8"),
            salt.encode("utf-8"),
            self.ITERACOES,
        )

        hash_hex = hash_bytes.hex()

        return (
            f"{self.PREFIXO}"
            f"${self.ITERACOES}"
            f"${salt}"
            f"${hash_hex}"
        )

    def verificar_pin(
        self,
        pin: str,
        hash_salvo: str,
    ) -> bool:
        try:
            partes = hash_salvo.split("$")

            if len(partes) != 4:
                return False

            prefixo = partes[0]
            iteracoes = int(partes[1])
            salt = partes[2]
            hash_esperado = partes[3]

            if prefixo != self.PREFIXO:
                return False

            hash_bytes = hashlib.pbkdf2_hmac(
                "sha256",
                pin.encode("utf-8"),
                salt.encode("utf-8"),
                iteracoes,
            )

            hash_calculado = hash_bytes.hex()

            return hmac.compare_digest(
                hash_calculado,
                hash_esperado,
            )

        except (
            TypeError,
            ValueError,
        ):
            return False

    def eh_hash(
        self,
        valor: str,
    ) -> bool:
        return str(valor).startswith(
            f"{self.PREFIXO}$"
        )


pin_service = PinService()