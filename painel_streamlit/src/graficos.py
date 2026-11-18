"""Construtores de figuras Plotly. Cada função recebe dados já agregados e devolve uma figura.

Regras aplicadas (skill de dataviz):
- um eixo y por gráfico (nada de eixo duplo); escalas diferentes viram painéis separados;
- cor segue a entidade (Feminino/Masculino sempre com a mesma cor), nunca a posição;
- rótulos diretos seletivos; legenda presente quando há 2+ séries;
- percentuais sempre com o denominador explícito no eixo ou no tooltip.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import config as C
from .formatos import n, pct


def _base(fig: go.Figure, titulo: str, altura: int = 380, subtitulo: str | None = None) -> go.Figure:
    """Título e subtítulo ficam em layout.meta e são escritos como texto acima do gráfico
    (componentes.grafico). O Plotly não quebra linha no título e cortava textos longos."""
    fig.update_layout(meta=dict(titulo=titulo, sub=subtitulo or ""),
                      height=max(200, altura - (70 if subtitulo else 44)),
                      margin=dict(t=34))
    return fig


# ---------------- Evolução temporal ----------------
def evolucao_mensal(mensal: pd.DataFrame, titulo: str, subtitulo: str) -> go.Figure:
    """Dois painéis com eixo x compartilhado: ocorrências e óbitos (escalas diferentes)."""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12,
                        row_heights=[0.55, 0.45],
                        subplot_titles=("Ocorrências por mês", "Óbitos por mês"))
    fig.add_trace(go.Scatter(
        x=mensal["mes_ref"], y=mensal["ocorrencias"], mode="lines",
        line=dict(color=C.COR["serie"], width=2), name="Ocorrências",
        hovertemplate="%{x|%b/%Y}<br><b>%{y:,.0f}</b> ocorrências<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=mensal["mes_ref"], y=mensal["obitos"], mode="lines",
        line=dict(color=C.COR_ESTADO["Óbito"], width=2), name="Óbitos",
        hovertemplate="%{x|%b/%Y}<br><b>%{y:,.0f}</b> óbitos<extra></extra>"), row=2, col=1)
    fig.update_yaxes(rangemode="tozero")
    fig.update_xaxes(tickformat="%b/%y", dtick="M3")
    fig.update_layout(showlegend=False, hovermode="x unified")
    for anot in fig.layout.annotations:
        anot.update(font=dict(size=12, color=C.COR["tinta_2"]), x=0, xanchor="left")
    return _base(fig, titulo, 470, subtitulo)


def linha_simples(x, y, titulo, subtitulo, rotulo_y, formato_hover, cor=None,
                  altura=340, texto_x=None, y_zero=True) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=x, y=y, mode="lines+markers", line=dict(color=cor or C.COR["serie"], width=2),
        marker=dict(size=7, color=cor or C.COR["serie"], line=dict(color=C.COR["superficie"], width=2)),
        hovertemplate=formato_hover + "<extra></extra>"))
    fig.update_yaxes(title=rotulo_y, rangemode="tozero" if y_zero else "normal")
    if texto_x:
        fig.update_xaxes(title=texto_x)
    fig.update_layout(showlegend=False, hovermode="x")
    return _base(fig, titulo, altura, subtitulo)


# ---------------- Composição ----------------
def barras_100(pct_tab: pd.DataFrame, contagem: pd.DataFrame, cores: dict, titulo: str,
               subtitulo: str, altura: int = 300, rotulo_min: float = 6.0) -> go.Figure:
    """Barras horizontais empilhadas a 100%: cada linha de `pct_tab` soma 100."""
    fig = go.Figure()
    linhas = [str(i) for i in pct_tab.index]
    for col in pct_tab.columns:
        valores = pct_tab[col].to_numpy()
        textos = [pct(v, 1) if v >= rotulo_min else "" for v in valores]
        cor = cores.get(col, C.COR["serie"])
        cor_texto = "#ffffff" if col not in ("Ileso", "Sem Vítimas") else C.COR["tinta"]
        fig.add_trace(go.Bar(
            y=linhas, x=valores, name=str(col), orientation="h",
            marker=dict(color=cor, line=dict(color=C.COR["superficie"], width=2)),
            text=textos, textposition="inside", insidetextanchor="middle",
            textfont=dict(color=cor_texto, size=12),
            customdata=np.stack([contagem[col].to_numpy()], axis=-1),
            hovertemplate="%{y} · " + str(col) + "<br><b>%{x:.1f}%</b> (%{customdata[0]:,.0f})<extra></extra>"))
    fig.update_layout(barmode="stack", bargap=0.35)
    fig.update_xaxes(range=[0, 100], ticksuffix="%", showgrid=False)
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_layout(legend=dict(traceorder="normal"))
    return _base(fig, titulo, altura, subtitulo)


# ---------------- Rankings ----------------
def ranking(serie: pd.Series, titulo: str, subtitulo: str, destaque: int = 0,
            formato: str = "n", altura: int | None = None, rotulo_x: str = "") -> go.Figure:
    """Barras horizontais ordenadas. `destaque` pinta os N primeiros e apaga o resto."""
    serie = serie.sort_values(ascending=True)
    total = len(serie)
    cores = [C.COR["serie"] if (destaque == 0 or i >= total - destaque) else C.COR["serie_apagada"]
             for i in range(total)]
    textos = [pct(v, 1) if formato == "pct" else n(v) for v in serie.values]
    rotulos = [str(i) if len(str(i)) <= 48 else str(i)[:47] + "…" for i in serie.index]
    fig = go.Figure(go.Bar(
        y=rotulos, x=serie.values, orientation="h",
        marker=dict(color=cores, line=dict(color=C.COR["superficie"], width=2)),
        text=textos, textposition="outside", cliponaxis=False,
        textfont=dict(color=C.COR["tinta_2"], size=12),
        customdata=[str(i) for i in serie.index],
        hovertemplate="%{customdata}<br><b>%{text}</b><extra></extra>"))
    fig.update_xaxes(showgrid=False, showticklabels=False, title=rotulo_x,
                     range=[0, float(serie.max()) * 1.18 if total else 1])
    fig.update_yaxes(showgrid=False)
    fig.update_layout(showlegend=False, margin=dict(r=40, t=12))
    return _base(fig, titulo, altura or max(260, 34 * total + 90), subtitulo)


# ---------------- Calendário ----------------
def mapa_calor(tab: pd.DataFrame, titulo: str, subtitulo: str, rotulo_valor: str,
               formato_valor: str = ",.0f") -> go.Figure:
    fig = go.Figure(go.Heatmap(
        z=tab.values, x=[str(c) for c in tab.columns], y=[str(i) for i in tab.index],
        colorscale=[[i / (len(C.RAMPA_SEQUENCIAL) - 1), c] for i, c in enumerate(C.RAMPA_SEQUENCIAL)],
        xgap=2, ygap=2,
        colorbar=dict(title=dict(text=rotulo_valor, side="right"), thickness=10, outlinewidth=0,
                      tickfont=dict(color=C.COR["tinta_muda"])),
        hovertemplate="%{y} · %{x}h<br><b>%{z:" + formato_valor + "}</b> " + rotulo_valor + "<extra></extra>"))
    fig.update_xaxes(title="Hora do dia", dtick=2, showgrid=False)
    fig.update_yaxes(autorange="reversed", showgrid=False)
    return _base(fig, titulo, 360, subtitulo)


def barras_simples(x, y, titulo, subtitulo, rotulo_y, hover, destaque_idx=None,
                   altura=320, formato_texto=None) -> go.Figure:
    cores = [C.COR["serie"]] * len(x)
    if destaque_idx is not None:
        cores = [C.COR["serie"] if i in destaque_idx else C.COR["serie_apagada"] for i in range(len(x))]
    fig = go.Figure(go.Bar(
        x=[str(v) for v in x], y=y, marker=dict(color=cores, line=dict(color=C.COR["superficie"], width=2)),
        text=formato_texto, textposition="outside", cliponaxis=False,
        textfont=dict(color=C.COR["tinta_2"], size=11),
        hovertemplate=hover + "<extra></extra>"))
    fig.update_yaxes(title=rotulo_y, rangemode="tozero")
    fig.update_layout(showlegend=False)
    return _base(fig, titulo, altura, subtitulo)


# ---------------- Mapa ----------------
def mapa_pontos(pontos: pd.DataFrame, titulo: str, subtitulo: str) -> go.Figure:
    """Pontos agregados numa grade de ~0,25°. Tamanho = ocorrências; cor = % fatais."""
    tam = 4 + 22 * np.sqrt(pontos["ocorrencias"] / max(pontos["ocorrencias"].max(), 1))
    marcador = dict(size=tam, color=pontos["pct_fatais"], cmin=0,
                    cmax=float(np.nanpercentile(pontos["pct_fatais"], 95)) if len(pontos) else 1,
                    colorscale=[[0, "#f3c9c2"], [0.5, "#de6b5c"], [1, "#6e1714"]],
                    opacity=0.72,
                    colorbar=dict(title=dict(text="% fatais", side="right"), thickness=10,
                                  outlinewidth=0, ticksuffix="%"))
    custom = list(zip(pontos["ocorrencias"].astype(int).tolist(), pontos["pct_fatais"].astype(float).tolist(),
                      pontos["local"].astype(str).tolist()))
    hover = "<b>%{customdata[2]}</b><br>%{customdata[0]:,.0f} ocorrências<br>%{customdata[1]:.1f}% com morte<extra></extra>"
    centro = dict(lat=-14.5, lon=-52)
    if hasattr(go, "Scattermap"):  # Plotly >= 5.24 (MapLibre, sem token)
        fig = go.Figure(go.Scattermap(lat=pontos["lat"], lon=pontos["lon"], mode="markers",
                                      marker=marcador, customdata=custom, hovertemplate=hover))
        fig.update_layout(map=dict(style="carto-positron", center=centro, zoom=3.0))
    else:  # versões antigas
        fig = go.Figure(go.Scattermapbox(lat=pontos["lat"], lon=pontos["lon"], mode="markers",
                                         marker=marcador, customdata=custom, hovertemplate=hover))
        fig.update_layout(mapbox=dict(style="carto-positron", center=centro, zoom=3.0))
    fig = _base(fig, titulo, 560, subtitulo)
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=8))
    return fig


# ---------------- Comparação por sexo ----------------
def barras_sexo(tab: pd.DataFrame, titulo: str, subtitulo: str, rotulo_x: str,
                altura: int | None = None, hover_n: pd.DataFrame | None = None) -> go.Figure:
    """Barras horizontais agrupadas: linhas = categorias, colunas = Feminino/Masculino (%)."""
    fig = go.Figure()
    linhas = [str(i) if len(str(i)) <= 46 else str(i)[:45] + "…" for i in tab.index]
    for sexo in [s for s in C.SEXOS if s in tab.columns]:
        cd = hover_n[sexo].to_numpy() if hover_n is not None else tab[sexo].to_numpy()
        fig.add_trace(go.Bar(
            y=linhas, x=tab[sexo], name=sexo, orientation="h",
            marker=dict(color=C.COR[sexo], line=dict(color=C.COR["superficie"], width=2)),
            customdata=cd, text=[pct(v, 1) for v in tab[sexo]], textposition="outside",
            cliponaxis=False, textfont=dict(size=11, color=C.COR["tinta_2"]),
            hovertemplate="%{y}<br>" + sexo + ": <b>%{x:.1f}%</b>"
                          + (" (%{customdata:,.0f})" if hover_n is not None else "") + "<extra></extra>"))
    fig.update_layout(barmode="group", bargap=0.3, bargroupgap=0.05)
    fig.update_xaxes(ticksuffix="%", title=rotulo_x, showgrid=True, gridcolor=C.COR["grade"],
                     range=[0, float(np.nanmax(tab.values)) * 1.2])
    fig.update_yaxes(autorange="reversed", showgrid=False)
    return _base(fig, titulo, altura or max(300, 52 * len(tab) + 110), subtitulo)


def linhas_sexo(tab: pd.DataFrame, titulo: str, subtitulo: str, rotulo_x: str, rotulo_y: str,
                altura: int = 360) -> go.Figure:
    """Uma linha por sexo (ex.: distribuição de idade em %), com rótulo direto no fim."""
    fig = go.Figure()
    for sexo in [s for s in C.SEXOS if s in tab.columns]:
        fig.add_trace(go.Scatter(
            x=tab.index, y=tab[sexo], name=sexo, mode="lines",
            line=dict(color=C.COR[sexo], width=2),
            hovertemplate="%{x}: <b>%{y:.2f}%</b> · " + sexo + "<extra></extra>"))
    fig.update_xaxes(title=rotulo_x)
    fig.update_yaxes(title=rotulo_y, ticksuffix="%", rangemode="tozero")
    fig.update_layout(hovermode="x unified")
    return _base(fig, titulo, altura, subtitulo)


def taxa_com_ic(taxas: pd.DataFrame, grupo: str, medida: str, titulo: str, subtitulo: str,
                rotulo_x: str, n_min: int = 100) -> go.Figure:
    """Pontos com IC 95% por grupo e sexo. Grupos com n < n_min ficam vazados (pouca evidência)."""
    ic_inf, ic_sup = ("let_ic_inf", "let_ic_sup") if medida == "letalidade" else ("grav_ic_inf", "grav_ic_sup")
    grupos = [g for g in taxas[grupo].astype("string").unique()]
    ordem = [g for g in (taxas[grupo].cat.categories if hasattr(taxas[grupo], "cat") else grupos)
             if g in set(grupos)]
    pos = {g: i for i, g in enumerate(ordem)}
    fig = go.Figure()
    for k, sexo in enumerate(C.SEXOS):
        d = taxas[taxas["sexo"] == sexo].copy()
        if d.empty:
            continue
        d["y"] = d[grupo].astype("string").map(pos) + (-0.17 if sexo == "Feminino" else 0.17)
        solido = d["n"] >= n_min
        for mascara, vazado in [(solido, False), (~solido, True)]:
            dd = d[mascara]
            if dd.empty:
                continue
            fig.add_trace(go.Scatter(
                x=dd[medida], y=dd["y"], mode="markers", name=sexo,
                legendgroup=sexo, showlegend=not vazado,
                marker=dict(size=10, color=C.COR["superficie"] if vazado else C.COR[sexo],
                            line=dict(color=C.COR[sexo], width=2), symbol="circle"),
                error_x=dict(type="data", symmetric=False, array=dd[ic_sup] - dd[medida],
                             arrayminus=dd[medida] - dd[ic_inf], color=C.COR[sexo], thickness=1.5, width=0),
                customdata=list(zip(dd[grupo].astype(str).tolist(), dd["n"].astype(int).tolist(),
                                    dd[ic_inf].astype(float).tolist(), dd[ic_sup].astype(float).tolist())),
                hovertemplate="%{customdata[0]} · " + sexo + "<br><b>%{x:.2f}%</b>"
                              " (IC 95%: %{customdata[2]:.2f}–%{customdata[3]:.2f})<br>"
                              "n = %{customdata[1]:,.0f} condutores<extra></extra>"))
    fig.update_yaxes(tickvals=list(range(len(ordem))), ticktext=ordem, autorange="reversed",
                     showgrid=False, range=[len(ordem) - 0.5, -0.5])
    fig.update_xaxes(title=rotulo_x, ticksuffix="%", showgrid=True, gridcolor=C.COR["grade"],
                     rangemode="tozero")
    for i in range(len(ordem)):
        if i % 2 == 0:
            fig.add_hrect(y0=i - 0.5, y1=i + 0.5, fillcolor=C.COR["plano"], line_width=0, layer="below")
    return _base(fig, titulo, max(320, 58 * len(ordem) + 120), subtitulo)


def floresta(res: pd.DataFrame, titulo: str, subtitulo: str, destaque: str = "sexo=Masculino") -> go.Figure:
    """Forest plot das razões de chance (escala log, referência em 1)."""
    d = res[res["termo"] != "(intercepto)"].copy()
    d["rotulo"] = d["termo"].str.replace("grupo_veiculo=", "Veículo: ", regex=False) \
        .str.replace("faixa_etaria=", "Idade: ", regex=False) \
        .str.replace("fase_dia=", "Fase do dia: ", regex=False) \
        .str.replace("uso_solo=Sim", "Trecho urbano", regex=False) \
        .str.replace("tipo_dia=", "", regex=False) \
        .str.replace("sexo=Masculino", "Sexo: Masculino", regex=False)
    d = d.iloc[::-1]
    cores = [C.COR["Masculino"] if t == destaque else C.COR["tinta_2"] for t in d["termo"]]
    fig = go.Figure(go.Scatter(
        x=d["or"], y=d["rotulo"], mode="markers",
        marker=dict(size=[13 if t == destaque else 8 for t in d["termo"]], color=cores,
                    symbol="square", line=dict(color=C.COR["superficie"], width=1)),
        error_x=dict(type="data", symmetric=False, array=d["ic_sup"] - d["or"],
                     arrayminus=d["or"] - d["ic_inf"], color=C.COR["tinta_muda"], thickness=1.5, width=0),
        customdata=np.stack([d["ic_inf"], d["ic_sup"], d["p"]], axis=-1),
        hovertemplate="%{y}<br>OR <b>%{x:.2f}</b> (IC 95%: %{customdata[0]:.2f}–%{customdata[1]:.2f})"
                      "<extra></extra>"))
    fig.add_vline(x=1, line=dict(color=C.COR["eixo"], width=1.5))
    fig.update_xaxes(type="log", title="Razão de chances ajustada (escala log) · 1 = sem diferença",
                     showgrid=True, gridcolor=C.COR["grade"], tickvals=[0.25, 0.5, 1, 2, 4, 8],
                     ticktext=["0,25", "0,5", "1", "2", "4", "8"])
    fig.update_yaxes(showgrid=False)
    fig.update_layout(showlegend=False)
    return _base(fig, titulo, 34 * len(d) + 140, subtitulo)
