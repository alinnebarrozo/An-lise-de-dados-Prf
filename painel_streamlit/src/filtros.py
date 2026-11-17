"""Lógica de filtros (sem Streamlit, para poder ser testada).

Regra de grão — escrita também no painel:
- Filtros de OCORRÊNCIA (data, local, rodovia, gravidade, tipo) recortam as duas tabelas.
- Filtros de PESSOA (sexo, faixa etária, tipo de envolvido) recortam os envolvidos.
  Quando algum está ativo, os KPIs de ocorrência passam a contar
  "ocorrências com ao menos um envolvido no recorte".
"""
from __future__ import annotations

from dataclasses import dataclass, fields, replace

import pandas as pd


@dataclass(frozen=True)
class Filtros:
    periodo: tuple | None = None          # (data_inicial, data_final)
    anos: tuple = ()
    meses: tuple = ()
    ufs: tuple = ()
    municipios: tuple = ()
    brs: tuple = ()
    classificacoes: tuple = ()
    tipos_acidente: tuple = ()
    sexos: tuple = ()
    faixas: tuple = ()
    tipos_envolvido: tuple = ()

    CAMPOS_PESSOA = ("sexos", "faixas", "tipos_envolvido")

    def sem(self, *campos: str) -> "Filtros":
        """Cópia com alguns filtros desligados (ex.: capítulo que compara os sexos)."""
        return replace(self, **{c: (None if c == "periodo" else ()) for c in campos})

    def com(self, **valores) -> "Filtros":
        return replace(self, **valores)

    def ativos(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)
                if getattr(self, f.name) not in ((), None)}

    def tem_filtro_pessoa(self) -> bool:
        return any(getattr(self, c) for c in self.CAMPOS_PESSOA)


def _mascara_ocorrencia(df: pd.DataFrame, f: Filtros) -> pd.Series:
    m = pd.Series(True, index=df.index)
    if f.periodo:
        ini, fim = pd.Timestamp(f.periodo[0]), pd.Timestamp(f.periodo[1])
        m &= df["data"].between(ini, fim)
    regras = [("anos", "ano"), ("meses", "mes"), ("ufs", "uf"), ("municipios", "municipio"),
              ("brs", "br"), ("classificacoes", "classificacao_acidente"),
              ("tipos_acidente", "tipo_acidente")]
    for campo, coluna in regras:
        valores = getattr(f, campo)
        if valores:
            m &= df[coluna].isin(valores)
    return m


def _mascara_pessoa(df: pd.DataFrame, f: Filtros) -> pd.Series:
    m = pd.Series(True, index=df.index)
    for campo, coluna in [("sexos", "sexo"), ("faixas", "faixa_etaria"),
                          ("tipos_envolvido", "tipo_envolvido")]:
        valores = getattr(f, campo)
        if valores:
            m &= df[coluna].isin(valores)
    return m


def aplicar(ocorrencias: pd.DataFrame, envolvidos: pd.DataFrame, f: Filtros):
    """Devolve (ocorrencias_filtradas, envolvidos_filtrados) respeitando os grãos."""
    oc = ocorrencias[_mascara_ocorrencia(ocorrencias, f)]
    ev = envolvidos[_mascara_ocorrencia(envolvidos, f) & _mascara_pessoa(envolvidos, f)]
    if f.tem_filtro_pessoa():
        oc = oc[oc["id"].isin(ev["id"].unique())]
    return oc, ev


ROTULOS = {
    "periodo": "Período", "anos": "Ano", "meses": "Mês", "ufs": "UF", "municipios": "Município",
    "brs": "BR", "classificacoes": "Gravidade", "tipos_acidente": "Tipo de acidente",
    "sexos": "Sexo", "faixas": "Faixa etária", "tipos_envolvido": "Envolvido",
}
