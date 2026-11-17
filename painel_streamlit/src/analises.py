"""Agregações usadas pelos capítulos (pandas puro, testáveis sem Streamlit)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C
from . import metricas as M


# ---------------- Capítulo 1 ----------------
def mensal(oc: pd.DataFrame, ev: pd.DataFrame) -> pd.DataFrame:
    a = oc.groupby(["ano", "mes"]).size().rename("ocorrencias")
    b = ev.groupby(["ano", "mes"])["obito"].sum().rename("obitos")
    d = pd.concat([a, b], axis=1).fillna(0).reset_index()
    d["mes_ref"] = pd.to_datetime(dict(year=d["ano"], month=d["mes"], day=1))
    return d.sort_values("mes_ref")


def classificacao_por_ano(oc: pd.DataFrame):
    return M.composicao(oc.dropna(subset=["classificacao_acidente"]), "ano",
                        "classificacao_acidente", C.ORDEM_CLASSIFICACAO)


def kpis_por_ano(oc: pd.DataFrame, ev: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for ano in sorted(oc["ano"].unique()):
        k = M.kpis(oc[oc["ano"] == ano], ev[ev["ano"] == ano])
        k["ano"] = ano
        k["meses"] = oc.loc[oc["ano"] == ano, "mes"].nunique()
        linhas.append(k)
    return pd.DataFrame(linhas)


def comparar_anos(oc: pd.DataFrame, ev: pd.DataFrame, ano_a: int, ano_b: int):
    """Compara dois anos na MESMA janela de meses (2026 vai só até agosto)."""
    meses_a = set(oc.loc[oc["ano"] == ano_a, "mes"].unique())
    meses_b = set(oc.loc[oc["ano"] == ano_b, "mes"].unique())
    meses = sorted(meses_a & meses_b)
    sel_o = oc["mes"].isin(meses)
    sel_e = ev["mes"].isin(meses)
    ka = M.kpis(oc[sel_o & (oc["ano"] == ano_a)], ev[sel_e & (ev["ano"] == ano_a)])
    kb = M.kpis(oc[sel_o & (oc["ano"] == ano_b)], ev[sel_e & (ev["ano"] == ano_b)])
    return ka, kb, meses


# ---------------- Capítulo 2 ----------------
def pontos_mapa(oc: pd.DataFrame, passo: float = 0.25) -> pd.DataFrame:
    d = oc.dropna(subset=["latitude", "longitude"])
    d = d[d["latitude"].between(-34.5, 5.5) & d["longitude"].between(-74.5, -32)]
    lat = (d["latitude"] / passo).round() * passo
    lon = (d["longitude"] / passo).round() * passo
    g = (d.assign(lat=lat, lon=lon)
         .groupby(["lat", "lon"], observed=True)
         .agg(ocorrencias=("id", "size"), fatais=("fatal", "sum"),
              local=("municipio", lambda s: s.astype("string").mode().iat[0] if len(s) else ""),
              uf=("uf", lambda s: s.astype("string").mode().iat[0] if len(s) else ""))
         .reset_index())
    g["pct_fatais"] = 100 * g["fatais"] / g["ocorrencias"]
    g["local"] = g["local"].astype(str) + " (" + g["uf"].astype(str) + ")"
    return g


def ranking_local(oc: pd.DataFrame, coluna: str, metrica: str, top: int = 10,
                  minimo: int = 200) -> pd.Series:
    g = oc.groupby(coluna, observed=True).agg(ocorrencias=("id", "size"), fatais=("fatal", "sum"))
    if coluna == "br":
        g.index = "BR-" + g.index.astype(int).astype(str).str.zfill(3)
    if coluna == "municipio":
        uf = oc.groupby("municipio", observed=True)["uf"].agg(lambda s: s.astype("string").mode().iat[0])
        g.index = [f"{m.title()} ({uf[m]})" for m in g.index]
    if metrica == "ocorrencias":
        return g["ocorrencias"].nlargest(top)
    g = g[g["ocorrencias"] >= minimo]
    return (100 * g["fatais"] / g["ocorrencias"]).nlargest(top)


def calor_dia_hora(oc: pd.DataFrame, metrica: str) -> pd.DataFrame:
    d = oc.dropna(subset=["hora"])
    if metrica == "ocorrencias":
        t = pd.crosstab(d["dia_semana"], d["hora"].astype(int))
    else:
        t = d.pivot_table(index="dia_semana", columns=d["hora"].astype(int), values="fatal",
                          aggfunc="mean", observed=True) * 100
    t = t.reindex([x for x in C.ORDEM_DIA if x in t.index])
    t.index = [C.DIA_CURTO[x] for x in t.index]
    return t


def por_fase(oc: pd.DataFrame) -> pd.DataFrame:
    g = (oc.dropna(subset=["fase_dia"]).groupby("fase_dia", observed=True)
         .agg(ocorrencias=("id", "size"), fatais=("fatal", "sum")).reset_index())
    g["pct_ocorrencias"] = 100 * g["ocorrencias"] / g["ocorrencias"].sum()
    g["pct_fatais"] = 100 * g["fatais"] / g["ocorrencias"]
    return g


def sazonalidade(oc: pd.DataFrame) -> tuple[pd.DataFrame, list[int]]:
    """Média de ocorrências por mês usando só anos completos (12 meses no recorte)."""
    meses_por_ano = oc.groupby("ano")["mes"].nunique()
    completos = sorted(meses_por_ano[meses_por_ano == 12].index.tolist())
    d = oc[oc["ano"].isin(completos)]
    if d.empty:
        return pd.DataFrame(columns=["mes", "media"]), completos
    g = d.groupby(["ano", "mes"]).size().groupby("mes").mean().rename("media").reset_index()
    return g, completos


# ---------------- Capítulos 3 e 4 ----------------
def participacao_feminina(ev: pd.DataFrame) -> pd.DataFrame:
    d = ev[ev["sexo"].isin(C.SEXOS)]
    t, p = M.composicao(d, "tipo_envolvido", "sexo", C.SEXOS)
    ordem = ["Condutor", "Passageiro", "Pedestre", "Testemunha", "Cavaleiro"]
    return t.reindex([o for o in ordem if o in t.index]), p.reindex([o for o in ordem if o in p.index])


def distribuicao_idade(ev: pd.DataFrame) -> pd.DataFrame:
    d = ev[ev["sexo"].isin(C.SEXOS) & ev["idade"].between(14, 90)]
    t = pd.crosstab(d["idade"].astype(int), d["sexo"])
    return (t / t.sum() * 100).reindex(columns=[s for s in C.SEXOS if s in t.columns])


def pct_por_sexo(ev: pd.DataFrame, coluna: str, top: int | None = None, ordem=None):
    """% dos envolvidos de cada sexo em cada categoria (cada sexo soma 100%)."""
    d = ev[ev["sexo"].isin(C.SEXOS)].dropna(subset=[coluna])
    t = pd.crosstab(d[coluna].astype("string"), d["sexo"].astype("string"))
    t = t.reindex(columns=[s for s in C.SEXOS if s in t.columns]).fillna(0)
    p = t / t.sum() * 100
    if ordem:
        idx = [o for o in ordem if o in p.index]
    else:
        idx = t.sum(axis=1).sort_values(ascending=False).index.tolist()
    if top:
        idx = idx[:top]
    return t.loc[idx], p.loc[idx]


def estado_por(ev: pd.DataFrame, linha: str, ordem_linha=None):
    d = ev.dropna(subset=["estado_fisico"])
    t, p = M.composicao(d, linha, "estado_fisico", C.ORDEM_ESTADO)
    if ordem_linha:
        keep = [o for o in ordem_linha if o in t.index]
        t, p = t.reindex(keep), p.reindex(keep)
    t.index = t.index.astype(str)
    p.index = p.index.astype(str)
    return t, p


def gravidade_todos_vs_condutores(ev: pd.DataFrame):
    d = ev[ev["sexo"].isin(C.SEXOS) & ev["estado_informado"]].copy()
    d["grupo"] = np.where(d["tipo_envolvido"] == "Condutor", "Condutores", "Todos os envolvidos")
    partes = []
    for nome, sub in [("Todos os envolvidos", d), ("Somente condutores", d[d["tipo_envolvido"] == "Condutor"])]:
        g = sub.groupby("sexo", observed=True).agg(n=("obito", "size"), obitos=("obito", "sum"))
        g["letalidade"] = 100 * g["obitos"] / g["n"]
        g["grupo"] = nome
        partes.append(g.reset_index())
    return pd.concat(partes, ignore_index=True)


def teste_sexo_estado(cond: pd.DataFrame):
    d = cond[cond["estado_informado"]]
    tab = pd.crosstab(d["sexo"], d["estado_fisico"]).reindex(columns=C.ORDEM_ESTADO).fillna(0)
    return tab, M.qui_quadrado(tab)


def causas_por_sexo(cond: pd.DataFrame, veiculo_unico: bool, top: int = 8):
    d = cond[cond["veiculo_unico"]] if veiculo_unico else cond
    t, p = pct_por_sexo(d, "causa_acidente", top=top)
    completa = pd.crosstab(d["causa_acidente"].astype("string"), d["sexo"].astype("string"))
    completa = completa[completa.sum(axis=1) >= 30]  # evita células esparsas no teste
    return t, p, M.qui_quadrado(completa)


def resumo_sexo(cond: pd.DataFrame) -> dict:
    """Letalidade, gravidade, risco relativo M/F entre condutores com estado informado."""
    tx = M.taxas_por(cond, ["sexo"]).set_index("sexo")
    out = {"taxas": tx}
    if {"Feminino", "Masculino"} <= set(tx.index.astype(str)):
        f, m = tx.loc["Feminino"], tx.loc["Masculino"]
        out["rr_obito"] = M.razao_de_risco(m["obitos"], m["n"], f["obitos"], f["n"]) if f["obitos"] > 0 else None
        out["rr_grave"] = M.razao_de_risco(m["graves"], m["n"], f["graves"], f["n"]) if f["graves"] > 0 else None
    return out


# ---------------- Capítulo 5: hipóteses (regras, para atualizar com novos dados) ----------------
def avaliar_hipoteses(ev_total: pd.DataFrame, reg_obito: pd.DataFrame, or_bruta_obito: dict) -> dict:
    cond = M.condutores_com_sexo(ev_total)
    share_f = 100 * (cond["sexo"] == "Feminino").mean()
    pas = ev_total[(ev_total["tipo_envolvido"] == "Passageiro") & ev_total["sexo"].isin(C.SEXOS)]
    share_f_pas = 100 * (pas["sexo"] == "Feminino").mean()

    res = resumo_sexo(cond)
    tx = res["taxas"]
    f, m = tx.loc["Feminino"], tx.loc["Masculino"]
    tab, teste = teste_sexo_estado(cond)
    if f["let_ic_sup"] < m["let_ic_inf"]:
        h2 = "nao_confirmada"
    elif f["let_ic_inf"] > m["let_ic_sup"]:
        h2 = "confirmada"
    else:
        h2 = "inconclusiva"

    _, _, teste_causa = causas_por_sexo(cond, veiculo_unico=True)
    h3 = "confirmada" if teste_causa and teste_causa["p"] < 0.05 else "inconclusiva"

    linha = reg_obito[reg_obito["termo"] == "sexo=Masculino"].iloc[0]
    if linha["ic_inf"] > 1:
        h4 = "confirmada"
    elif linha["ic_sup"] < 1:
        h4 = "confirmada"
    else:
        h4 = "inconclusiva"

    # estratos (veículo) em que a condutora tem letalidade maior que o condutor, com n suficiente
    estr = M.taxas_por(cond, ["grupo_veiculo", "sexo"])
    piv = estr.pivot_table(index="grupo_veiculo", columns="sexo", values=["letalidade", "n"], observed=True)
    validos = piv[(piv[("n", "Feminino")] >= 100) & (piv[("n", "Masculino")] >= 100)]
    m_maior = validos[("letalidade", "Masculino")] > validos[("letalidade", "Feminino")]
    estratos_m_maior = int(m_maior.sum())
    excecoes = [(str(g), int(validos.loc[g, ("n", "Feminino")])) for g in validos.index[~m_maior.to_numpy()]]

    return {
        "share_f_condutores": share_f, "share_f_passageiros": share_f_pas,
        "n_condutores": len(cond),
        "let_f": f["letalidade"], "let_m": m["letalidade"],
        "let_f_ic": (f["let_ic_inf"], f["let_ic_sup"]), "let_m_ic": (m["let_ic_inf"], m["let_ic_sup"]),
        "grav_f": f["gravidade"], "grav_m": m["gravidade"],
        "rr_obito": res.get("rr_obito"), "teste_estado": teste, "teste_causa": teste_causa,
        "or_ajustada": linha.to_dict(), "or_bruta": or_bruta_obito,
        "estratos_validos": len(validos), "estratos_m_maior": estratos_m_maior, "excecoes": excecoes,
        "veredito": {"H1": "inconclusiva", "H2": h2, "H3": h3, "H4": h4},
    }
