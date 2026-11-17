"""Blocos de interface reutilizáveis (Streamlit + HTML do tema)."""
from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from . import config as C
from .filtros import ROTULOS, Filtros
from .formatos import n

CONFIG_PLOTLY = {"displaylogo": False,
                 "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"],
                 "toImageButtonOptions": {"format": "png", "scale": 2}}


def html_bloco(conteudo: str) -> None:
    st.markdown(conteudo, unsafe_allow_html=True)


def hero(data_min, data_max) -> None:
    html_bloco(f"""
    <div class="hero">
      <div class="eyebrow">Data storytelling · Acidentes nas rodovias federais</div>
      <h1>“Mulher no volante, perigo constante?”</h1>
      <p>Uma viagem de cinco quilômetros pelos dados da PRF, de {data_min:%m/%Y} a {data_max:%m/%Y},
      para testar uma crença popular com evidência — e separar o que os dados mostram
      do que eles não conseguem mostrar.</p>
    </div>""")


def recorte(f: Filtros, n_oc: int, n_ev: int, avisos: list[str] | None = None) -> None:
    chips = [f'<span class="chip"><b>{n(n_oc)}</b> ocorrências</span>',
             f'<span class="chip"><b>{n(n_ev)}</b> envolvidos</span>']
    ativos = f.ativos()
    if not ativos:
        chips.append('<span class="chip">Sem filtros: base completa</span>')
    for campo, valor in ativos.items():
        if campo == "periodo":
            texto = f"{pd.Timestamp(valor[0]):%d/%m/%Y} – {pd.Timestamp(valor[1]):%d/%m/%Y}"
        elif campo == "meses":
            texto = ", ".join(C.MESES[m - 1] for m in valor)
        else:
            vals = [str(v) for v in valor]
            texto = ", ".join(vals[:3]) + (f" +{len(vals) - 3}" if len(vals) > 3 else "")
        chips.append(f'<span class="chip">{ROTULOS[campo]}: <b>{html.escape(texto)}</b></span>')
    for aviso in avisos or []:
        chips.append(f'<span class="chip" style="border-color:#f3d48a;background:#fff8e6">{aviso}</span>')
    html_bloco(f'<div class="recorte"><span class="rot">Recorte atual</span>{"".join(chips)}</div>')


def marco(km: str, titulo: str, pergunta: str, contexto: str) -> None:
    numero = km.split()[-1]
    html_bloco(f"""
    <div class="marco">
      <div class="km"><small>KM</small><span>{numero}</span></div>
      <div><h2>{titulo}</h2><div class="pergunta">{pergunta}</div></div>
    </div>
    <div class="contexto">{contexto}</div>""")


def kpis(cards: list[dict]) -> None:
    """cards: [{'rot':..., 'val':..., 'sub':..., 'delta':...}]"""
    partes = []
    for c in cards:
        delta = f'<div class="delta">{c["delta"]}</div>' if c.get("delta") else ""
        sub = f'<div class="sub">{c["sub"]}</div>' if c.get("sub") else ""
        partes.append(f'<div class="kpi"><div class="rot">{c["rot"]}</div>'
                      f'<div class="val">{c["val"]}</div>{sub}{delta}</div>')
    html_bloco(f'<div class="kpis">{"".join(partes)}</div>')


def leitura(texto: str, titulo: str = "O que os dados revelam") -> None:
    html_bloco(f'<div class="leitura"><h4>{titulo}</h4>{texto}</div>')


def descoberta(texto: str) -> None:
    html_bloco(f'<div class="descoberta"><span class="tag">Descoberta</span>{texto}</div>')


def nota(texto: str) -> None:
    html_bloco(f'<div class="nota">{texto}</div>')


def grafico(fig, dados: pd.DataFrame | None = None, chave: str | None = None) -> None:
    """Mostra a figura e, se houver, a tabela por trás dela (acessível sem passar o mouse)."""
    st.plotly_chart(fig, use_container_width=True, config=CONFIG_PLOTLY, key=chave)
    if dados is not None:
        with st.expander("Ver os números deste gráfico"):
            st.dataframe(dados, use_container_width=True, hide_index=isinstance(dados.index, pd.RangeIndex))


SELO = {"confirmada": ("✓", "Confirmada"), "nao_confirmada": ("✕", "Não confirmada"),
        "inconclusiva": ("?", "Inconclusiva")}


def hipotese(cod: str, titulo: str, veredito: str, explicacao: str, evidencia: str) -> None:
    icone, rotulo = SELO[veredito]
    html_bloco(f"""
    <div class="hip">
      <div class="topo"><span class="id">{cod}</span>
        <span class="selo {veredito}" role="status">{icone} {rotulo}</span></div>
      <h3>{titulo}</h3><p>{explicacao}</p>
      <div class="ev">{evidencia}</div>
    </div>""")


def sem_dados() -> None:
    st.info("Nenhum registro no recorte atual. Afrouxe algum filtro na barra lateral "
            "ou use **Limpar filtros**.")


def legenda_sexo() -> str:
    return (f'<span class="ponto" style="background:{C.COR["Feminino"]}"></span><span class="lg-f">Feminino</span> '
            f'&nbsp; <span class="ponto" style="background:{C.COR["Masculino"]}"></span><span class="lg-m">Masculino</span>')
