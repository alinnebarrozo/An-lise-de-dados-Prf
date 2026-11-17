"""Carga do modelo estrela exportado pelo notebook de ETL e montagem das tabelas analíticas.

O painel não refaz o ETL: lê os parquets de `dados/` e só junta as dimensões aos fatos.
Para atualizar os dados, rode o notebook de novo e substitua os arquivos da pasta.

Grãos (não misturar):
- `ocorrencias`: 1 linha por acidente (id)            -> KPIs de ocorrência
- `envolvidos`:  1 linha por pessoa envolvida (pesid)  -> KPIs de pessoa, perfil, gênero
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import pandas as pd

from . import config as C


def _ler(nome: str) -> pd.DataFrame:
    """Lê uma tabela do modelo estrela. PRF_FORMATO=pkl é usado só nos testes locais."""
    if os.environ.get("PRF_FORMATO") == "pkl":
        return pd.read_pickle(C.PASTA_DADOS / f"{nome}.pkl")
    return pd.read_parquet(C.PASTA_DADOS / f"{nome}.parquet")


@dataclass(frozen=True)
class Base:
    ocorrencias: pd.DataFrame
    envolvidos: pd.DataFrame
    qualidade: pd.DataFrame
    kpis: pd.DataFrame
    data_min: pd.Timestamp
    data_max: pd.Timestamp


def _categoria(serie: pd.Series, ordem: list[str] | None = None) -> pd.Series:
    serie = serie.astype("string")
    if ordem:
        extras = sorted(set(serie.dropna().unique()) - set(ordem))
        return pd.Categorical(serie, categories=ordem + extras, ordered=True)
    return serie.astype("category")


def carregar_base() -> Base:
    t = {nome: _ler(nome) for nome in C.TABELAS}

    dim_data = t["dim_data"].copy()
    dim_data["data"] = pd.to_datetime(dim_data["data"])

    # ---------- Ocorrências: fato + dimensões ----------
    oc = (t["fato_ocorrencia"]
          .merge(dim_data, on="sk_data", how="left", validate="many_to_one")
          .merge(t["dim_local"], on="sk_local", how="left", validate="many_to_one")
          .merge(t["dim_causa"], on="sk_causa", how="left", validate="many_to_one")
          .merge(t["dim_tipo_acidente"], on="sk_tipo", how="left", validate="many_to_one"))
    assert len(oc) == len(t["fato_ocorrencia"]), "Junção duplicou ocorrências"

    oc["fatal"] = (oc["mortos"] > 0).astype("int8")
    oc["data"] = pd.to_datetime(oc["data"])
    oc["dia_semana"] = _categoria(oc["dia_semana"], C.ORDEM_DIA)
    oc["fase_dia"] = _categoria(oc["fase_dia"], C.ORDEM_FASE)
    oc["classificacao_acidente"] = _categoria(oc["classificacao_acidente"], C.ORDEM_CLASSIFICACAO)
    for col in ["uf", "municipio", "causa_acidente", "tipo_acidente", "condicao_metereologica",
                "tipo_pista", "tracado_via", "uso_solo", "tipo_dia"]:
        oc[col] = _categoria(oc[col])
    oc["hora"] = pd.to_numeric(oc["hora"], errors="coerce")

    # ---------- Envolvidos: fato + atributos da ocorrência ----------
    cols_oc = ["id", "data", "ano", "mes", "dia_semana", "tipo_dia", "hora", "fase_dia",
               "uf", "municipio", "br", "causa_acidente", "tipo_acidente",
               "classificacao_acidente", "veiculos", "uso_solo", "condicao_metereologica",
               "tipo_pista"]
    ev = t["fato_envolvido"].drop(columns=["sk_data", "sk_local", "sk_causa", "sk_tipo"])
    ev = ev.merge(oc[cols_oc], on="id", how="left", validate="many_to_one")
    assert len(ev) == len(t["fato_envolvido"]), "Junção duplicou envolvidos"

    ev["sexo"] = _categoria(ev["sexo"], C.SEXOS)
    ev["estado_fisico"] = _categoria(ev["estado_fisico"], C.ORDEM_ESTADO)
    ev["faixa_etaria"] = _categoria(ev["faixa_etaria"], C.ORDEM_FAIXA)
    ev["tipo_envolvido"] = _categoria(ev["tipo_envolvido"])
    ev["tipo_veiculo"] = _categoria(ev["tipo_veiculo"])
    grupo = ev["tipo_veiculo"].astype("string").map(C.GRUPO_VEICULO).fillna("Outros")
    ev["grupo_veiculo"] = _categoria(grupo, C.ORDEM_VEICULO)
    ev["idade"] = pd.to_numeric(ev["idade"], errors="coerce")
    # Achado do painel (não estava na EDA): ~27 mil CONDUTORES com idade 0 (4,8 mil com sexo informado). É valor padrão
    # de preenchimento, não idade real. Nas análises de idade eles viram "não informado".
    # Passageiros com idade 0 (bebês) continuam válidos.
    idade_padrao = (ev["tipo_envolvido"] == "Condutor") & (ev["idade"] == 0)
    ev["idade_padrao_condutor"] = idade_padrao
    ev.loc[idade_padrao, "idade"] = pd.NA
    ev["faixa_etaria"] = ev["faixa_etaria"].mask(idade_padrao)
    ev["veiculo_unico"] = ev["veiculos"] == 1
    ev["estado_informado"] = ev["estado_fisico"].notna()

    qualidade = pd.read_csv(C.PASTA_DADOS / "registro_qualidade.csv")
    kpis = pd.read_csv(C.PASTA_DADOS / "dicionario_kpis.csv")

    return Base(ocorrencias=oc, envolvidos=ev, qualidade=qualidade, kpis=kpis,
                data_min=oc["data"].min(), data_max=oc["data"].max())


def assinatura_dados() -> str:
    """Muda quando algum arquivo de dados muda — usada como chave do cache."""
    partes = []
    for arq in sorted(C.PASTA_DADOS.glob("*")):
        partes.append(f"{arq.name}:{arq.stat().st_mtime_ns}")
    return "|".join(partes)
