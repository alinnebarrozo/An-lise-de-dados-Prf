"""Painel “Mulher no volante, perigo constante?” — dados de acidentes da PRF (2024–2026).

Execução:  streamlit run app.py
Dados:     parquets do modelo estrela gerados pelo notebook de ETL, na pasta dados/
"""
from __future__ import annotations

import streamlit as st

from src import analises as A
from src import componentes as UI
from src import config as C
from src import metricas as M
from src.capitulos import (cap1_cenario, cap2_onde_quando, cap3_quem,
                           cap4_diferencas, cap5_descobertas)
from src.contexto import Contexto
from src.dados import assinatura_dados, carregar_base
from src.filtros import Filtros, aplicar
from src.tema import CSS, registrar_template

st.set_page_config(page_title="Mulher no volante, perigo constante? · PRF",
                   page_icon="🛣️", layout="wide", initial_sidebar_state="expanded")
registrar_template()
st.markdown(CSS, unsafe_allow_html=True)


# ---------------- Carga (cache invalida quando os arquivos mudam) ----------------
@st.cache_resource(show_spinner="Carregando o modelo estrela…")
def base_em_cache(_assinatura: str):
    return carregar_base()


@st.cache_resource(show_spinner="Ajustando o modelo estatístico…")
def extras_em_cache(_assinatura: str):
    base = base_em_cache(_assinatura)
    reg = M.modelo_ajustado(base.envolvidos, "obito")
    bruta = M.or_bruta(base.envolvidos, "obito")
    return {"regressao": reg, "or_bruta": bruta,
            "hipoteses": A.avaliar_hipoteses(base.envolvidos, reg, bruta)}


assinatura = assinatura_dados()
base = base_em_cache(assinatura)
extras = extras_em_cache(assinatura)
oc_all, ev_all = base.ocorrencias, base.envolvidos

# ---------------- Filtros (barra lateral) ----------------
CHAVES = ["f_periodo", "f_anos", "f_meses", "f_ufs", "f_mun", "f_brs", "f_classif", "f_tipo",
          "f_sexo", "f_faixa", "f_envolvido"]


def limpar_filtros():
    for k in CHAVES:
        st.session_state.pop(k, None)


def opcoes(serie, ordem=None):
    valores = [v for v in serie.dropna().astype(str).unique()]
    if ordem:
        return [o for o in ordem if o in valores] + sorted(set(valores) - set(ordem))
    return sorted(valores)


with st.sidebar:
    st.markdown("## Filtros")
    st.button("↺  Limpar filtros", on_click=limpar_filtros, use_container_width=True, type="secondary")
    st.caption("Todos os gráficos e indicadores respondem aos filtros, que podem ser combinados.")

    st.markdown("**Quando**")
    d_min, d_max = base.data_min.date(), base.data_max.date()
    periodo = st.date_input("Período", value=(d_min, d_max), min_value=d_min, max_value=d_max,
                            format="DD/MM/YYYY", key="f_periodo")
    anos = st.multiselect("Ano", sorted(oc_all["ano"].unique().tolist()), key="f_anos",
                          placeholder="Todos")
    meses = st.multiselect("Mês", list(range(1, 13)), format_func=lambda m: C.MESES[m - 1],
                           key="f_meses", placeholder="Todos")

    st.markdown("**Onde**")
    ufs = st.multiselect("UF", opcoes(oc_all["uf"]), key="f_ufs", placeholder="Todas")
    mun_base = oc_all[oc_all["uf"].isin(ufs)] if ufs else oc_all
    municipios = st.multiselect("Município", opcoes(mun_base["municipio"]), key="f_mun",
                                placeholder="Todos (digite para buscar)")
    brs = st.multiselect("Rodovia (BR)", sorted(oc_all["br"].unique().tolist()), key="f_brs",
                         format_func=lambda b: f"BR-{int(b):03d}", placeholder="Todas")

    st.markdown("**Ocorrência**")
    classif = st.multiselect("Gravidade do acidente", opcoes(oc_all["classificacao_acidente"],
                                                            C.ORDEM_CLASSIFICACAO),
                             key="f_classif", placeholder="Todas")
    tipos = st.multiselect("Tipo de acidente", opcoes(oc_all["tipo_acidente"]), key="f_tipo",
                           placeholder="Todos")

    st.markdown("**Pessoa**")
    sexos = st.multiselect("Sexo", C.SEXOS, key="f_sexo", placeholder="Ambos")
    faixas = st.multiselect("Faixa etária", C.ORDEM_FAIXA, key="f_faixa", placeholder="Todas")
    envolvidos = st.multiselect("Tipo de envolvido", opcoes(ev_all["tipo_envolvido"]),
                                key="f_envolvido", placeholder="Todos")
    st.caption("Filtros de pessoa recortam os envolvidos. Os indicadores de ocorrência passam a contar "
               "acidentes com ao menos uma pessoa no recorte.")

periodo_valido = None
if isinstance(periodo, (tuple, list)) and len(periodo) == 2:
    if (periodo[0], periodo[1]) != (d_min, d_max):
        periodo_valido = (periodo[0], periodo[1])

filtros = Filtros(periodo=periodo_valido, anos=tuple(anos), meses=tuple(meses), ufs=tuple(ufs),
                  municipios=tuple(municipios), brs=tuple(brs), classificacoes=tuple(classif),
                  tipos_acidente=tuple(tipos), sexos=tuple(sexos), faixas=tuple(faixas),
                  tipos_envolvido=tuple(envolvidos))
oc, ev = aplicar(oc_all, ev_all, filtros)
ctx = Contexto(base=base, filtros=filtros, oc=oc, ev=ev, extra=extras)

# ---------------- Cabeçalho e navegação ----------------
UI.hero(base.data_min, base.data_max)
UI.recorte(filtros, len(oc), len(ev))

ROTULOS_NAV = [f"{km} · {titulo}" for _, km, titulo in C.CAPITULOS]
if "capitulo" not in st.session_state:
    st.session_state["capitulo"] = ROTULOS_NAV[0]


def ir_para(indice: int):
    st.session_state["capitulo"] = ROTULOS_NAV[indice]


escolha = st.segmented_control("Capítulo", ROTULOS_NAV, key="capitulo", label_visibility="collapsed")
if escolha is None:
    escolha = ROTULOS_NAV[0]
indice = ROTULOS_NAV.index(escolha)

RENDER = [cap1_cenario.render, cap2_onde_quando.render, cap3_quem.render,
          cap4_diferencas.render, cap5_descobertas.render]
RENDER[indice](ctx)

# ---------------- Avançar na história ----------------
st.write("")
c_ant, _, c_prox = st.columns([1, 2, 1])
if indice > 0:
    c_ant.button(f"← {ROTULOS_NAV[indice - 1]}", on_click=ir_para, args=(indice - 1,),
                 use_container_width=True)
if indice < len(ROTULOS_NAV) - 1:
    c_prox.button(f"{ROTULOS_NAV[indice + 1]} →", on_click=ir_para, args=(indice + 1,),
                  use_container_width=True, type="primary")

UI.html_bloco(f'<div class="rodape">{C.FONTE_DADOS} · Painel construído em Python, Streamlit e Plotly · '
              f'Dados até {base.data_max:%d/%m/%Y}.</div>')
