"""Objeto passado a cada capítulo: base completa, filtros e o recorte já aplicado."""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .dados import Base
from .filtros import Filtros, aplicar


@dataclass
class Contexto:
    base: Base
    filtros: Filtros
    oc: pd.DataFrame
    ev: pd.DataFrame
    extra: dict = field(default_factory=dict)

    def recorte(self, filtros: Filtros):
        """Recalcula o recorte com outro conjunto de filtros (ex.: ignorando o sexo)."""
        return aplicar(self.base.ocorrencias, self.base.envolvidos, filtros)
