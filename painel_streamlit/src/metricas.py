"""Indicadores e testes estatísticos.

As definições seguem o dicionário de KPIs do notebook (`dados/dicionario_kpis.csv`):
- Taxa de letalidade = óbitos ÷ envolvidos com estado físico informado
- Índice de gravidade = (óbitos + lesões graves) ÷ envolvidos com estado físico informado
- % de ocorrências fatais = ocorrências com mortos > 0 ÷ ocorrências
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from . import config as C


# ---------------- KPIs ----------------
def kpis(oc: pd.DataFrame, ev: pd.DataFrame) -> dict:
    informados = int(ev["estado_informado"].sum())
    obitos = int(ev["obito"].sum())
    graves = int(ev["vitima_grave"].sum())
    n_oc = len(oc)
    return {
        "ocorrencias": n_oc,
        "envolvidos": len(ev),
        "obitos": obitos,
        "ocorrencias_fatais": int(oc["fatal"].sum()),
        "pct_ocorrencias_fatais": 100 * oc["fatal"].mean() if n_oc else np.nan,
        "letalidade": 100 * obitos / informados if informados else np.nan,
        "gravidade": 100 * graves / informados if informados else np.nan,
        "estado_informado": informados,
    }


def wilson(sucessos, total, z: float = 1.96):
    """Intervalo de confiança de Wilson (95%) para uma proporção, em %."""
    sucessos = np.asarray(sucessos, dtype=float)
    total = np.asarray(total, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        p = sucessos / total
        den = 1 + z ** 2 / total
        centro = (p + z ** 2 / (2 * total)) / den
        meia = z * np.sqrt(p * (1 - p) / total + z ** 2 / (4 * total ** 2)) / den
    return 100 * (centro - meia), 100 * (centro + meia)


def taxas_por(ev: pd.DataFrame, grupos: list[str]) -> pd.DataFrame:
    """Letalidade e índice de gravidade (com IC 95%) por grupo, só com estado informado."""
    base = ev[ev["estado_informado"]]
    g = (base.groupby(grupos, observed=True)
         .agg(n=("obito", "size"), obitos=("obito", "sum"), graves=("vitima_grave", "sum"))
         .reset_index())
    g["letalidade"] = 100 * g["obitos"] / g["n"]
    g["gravidade"] = 100 * g["graves"] / g["n"]
    g["let_ic_inf"], g["let_ic_sup"] = wilson(g["obitos"], g["n"])
    g["grav_ic_inf"], g["grav_ic_sup"] = wilson(g["graves"], g["n"])
    return g


def composicao(df: pd.DataFrame, linha: str, coluna: str, ordem_coluna=None) -> pd.DataFrame:
    """Contagem e % dentro de cada valor de `linha` (cada linha soma 100%)."""
    t = pd.crosstab(df[linha], df[coluna])
    if ordem_coluna:
        t = t.reindex(columns=[c for c in ordem_coluna if c in t.columns])
    pct = t.div(t.sum(axis=1), axis=0) * 100
    return t, pct


# ---------------- Testes ----------------
def qui_quadrado(tabela: pd.DataFrame) -> dict | None:
    """Qui-quadrado de independência + V de Cramér (tamanho do efeito)."""
    tabela = tabela.loc[tabela.sum(axis=1) > 0, tabela.sum(axis=0) > 0]
    if tabela.shape[0] < 2 or tabela.shape[1] < 2:
        return None
    qui2, p, gl, esperado = stats.chi2_contingency(tabela)
    n = tabela.values.sum()
    v = float(np.sqrt(qui2 / (n * (min(tabela.shape) - 1))))
    return {"qui2": float(qui2), "p": float(p), "gl": int(gl), "n": int(n), "v": v,
            "esperado_min": float(esperado.min()), "efeito": rotulo_efeito(v)}


def rotulo_efeito(v: float) -> str:
    if v < 0.1:
        return "muito pequeno"
    if v < 0.3:
        return "pequeno"
    if v < 0.5:
        return "moderado"
    return "grande"


def razao_de_risco(a_eventos, a_total, b_eventos, b_total) -> dict:
    """Risco relativo A/B com IC 95% (método log)."""
    ra, rb = a_eventos / a_total, b_eventos / b_total
    rr = ra / rb
    ep = np.sqrt(1 / a_eventos - 1 / a_total + 1 / b_eventos - 1 / b_total)
    return {"rr": rr, "ic_inf": float(np.exp(np.log(rr) - 1.96 * ep)),
            "ic_sup": float(np.exp(np.log(rr) + 1.96 * ep))}


# ---------------- Regressão logística (IRLS, sem dependências extras) ----------------
def regressao_logistica(df: pd.DataFrame, desfecho: str, preditoras: list[str],
                        referencias: dict[str, str]) -> pd.DataFrame:
    """Ajusta logit(P(desfecho)) ~ preditoras categóricas e devolve razões de chance (OR) com IC 95%.

    Implementada com IRLS em NumPy para não exigir statsmodels. Linhas com ausentes são descartadas.
    """
    dados = df[[desfecho] + preditoras].dropna()
    blocos, nomes = [np.ones((len(dados), 1))], ["(intercepto)"]
    for var in preditoras:
        serie = dados[var].astype("string")
        niveis = [n for n in pd.unique(serie) if n != referencias[var]]
        niveis = sorted(niveis)
        for nivel in niveis:
            blocos.append((serie == nivel).to_numpy(dtype=float)[:, None])
            nomes.append(f"{var}={nivel}")
    X = np.hstack(blocos)
    y = dados[desfecho].to_numpy(dtype=float)

    beta = np.zeros(X.shape[1])
    for _ in range(50):
        eta = X @ beta
        mu = 1 / (1 + np.exp(-eta))
        w = np.clip(mu * (1 - mu), 1e-10, None)
        z = eta + (y - mu) / w
        XtW = X.T * w
        novo = np.linalg.solve(XtW @ X, XtW @ z)
        if np.max(np.abs(novo - beta)) < 1e-8:
            beta = novo
            break
        beta = novo
    mu = 1 / (1 + np.exp(-(X @ beta)))
    cov = np.linalg.inv((X.T * (mu * (1 - mu))) @ X)
    ep = np.sqrt(np.diag(cov))
    zstat = beta / ep
    res = pd.DataFrame({
        "termo": nomes, "coef": beta, "ep": ep,
        "or": np.exp(beta), "ic_inf": np.exp(beta - 1.96 * ep), "ic_sup": np.exp(beta + 1.96 * ep),
        "p": 2 * stats.norm.sf(np.abs(zstat)),
    })
    res.attrs["n"] = len(dados)
    res.attrs["eventos"] = int(y.sum())
    return res


def condutores_com_sexo(ev: pd.DataFrame) -> pd.DataFrame:
    return ev[(ev["tipo_envolvido"] == "Condutor") & ev["sexo"].isin(C.SEXOS)]


def modelo_ajustado(ev: pd.DataFrame, desfecho: str = "obito") -> pd.DataFrame:
    """Modelo da H4: o sexo continua associado ao desfecho quando ajustamos por
    tipo de veículo, faixa etária, fase do dia, uso do solo e tipo de dia?"""
    base = condutores_com_sexo(ev)
    base = base[base["estado_informado"] & (base["grupo_veiculo"] != "Outros")].copy()
    preditoras = ["sexo", "grupo_veiculo", "faixa_etaria", "fase_dia", "uso_solo", "tipo_dia"]
    refs = {"sexo": "Feminino", "grupo_veiculo": "Automóvel", "faixa_etaria": "35-44",
            "fase_dia": "Pleno dia", "uso_solo": "Não", "tipo_dia": "Dia útil"}
    return regressao_logistica(base, desfecho, preditoras, refs)


def or_bruta(ev: pd.DataFrame, desfecho: str = "obito") -> dict:
    """Razão de chances sem ajuste (Masculino vs Feminino), mesma população do modelo."""
    base = condutores_com_sexo(ev)
    base = base[base["estado_informado"] & (base["grupo_veiculo"] != "Outros")]
    base = base.dropna(subset=["faixa_etaria", "fase_dia", "uso_solo", "tipo_dia"])
    res = regressao_logistica(base, desfecho, ["sexo"], {"sexo": "Feminino"})
    linha = res[res["termo"] == "sexo=Masculino"].iloc[0]
    return linha.to_dict()
