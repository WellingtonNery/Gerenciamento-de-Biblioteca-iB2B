"""Resultado padrão das operações do sistema.

Toda operação de caso de uso devolve um Resultado em vez de deixar
exceções cruas atravessarem a fachada (regra 2 do planejamento).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Resultado:
    """Saída uniforme de qualquer caso de uso: sucesso ou recusa com motivo."""

    sucesso: bool
    mensagem: str
    dados: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(cls, mensagem: str, **dados: Any) -> "Resultado":
        """Operação concluída. Os dados extras vão no dicionário."""
        return cls(sucesso=True, mensagem=mensagem, dados=dados)

    @classmethod
    def recusado(cls, mensagem: str, **dados: Any) -> "Resultado":
        """Regra de negócio recusou a operação (não é erro de programa)."""
        return cls(sucesso=False, mensagem=mensagem, dados=dados)
