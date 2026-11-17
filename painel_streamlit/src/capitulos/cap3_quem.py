"""KM 3 — Quem se envolve nos acidentes."""
import streamlit as st

from .. import analises as A
from .. import componentes as UI
from .. import config as C
from .. import graficos as G
from .. import metricas as M
from ..formatos import n, pct


def render(ctx) -> None:
    ev = ctx.ev
    UI.marco("KM 3", "Quem se envolve",
             "Qual é o perfil das pessoas envolvidas — e onde estão as mulheres?",
             "A crença popular fala de quem <b>dirige</b>. Mas a base da PRF registra condutores, passageiros, "
             "pedestres e testemunhas. Antes de comparar homens e mulheres, é preciso ver em que papel cada "
             "um aparece, porque isso muda a leitura de qualquer indicador. " + UI.legenda_sexo())
    if ev.empty:
        UI.sem_dados()
        return

    cont, part = A.participacao_feminina(ev)
    cond = M.condutores_com_sexo(ev)
    sexo_inf = 100 * ev["sexo"].notna().mean()
    cards = [{"rot": "Envolvidos com sexo informado", "val": pct(sexo_inf),
              "sub": f"{n(ev['sexo'].isna().sum())} sem informação ficam fora dos %"}]
    for papel in ["Condutor", "Passageiro", "Pedestre"]:
        if papel in part.index and "Feminino" in part.columns:
            plural = {"Condutor": "condutores", "Passageiro": "passageiros", "Pedestre": "pedestres"}[papel]
            cards.append({"rot": f"Mulheres entre {plural}",
                          "val": pct(part.loc[papel, "Feminino"]),
                          "sub": f"{n(cont.loc[papel, 'Feminino'])} de {n(cont.loc[papel].sum())}"})
    UI.kpis(cards)

    # ---------- Papel na ocorrência ----------
    if len(part) and "Feminino" in part.columns:
        f_cond = part.loc["Condutor", "Feminino"] if "Condutor" in part.index else None
        f_pas = part.loc["Passageiro", "Feminino"] if "Passageiro" in part.index else None
        if f_cond is not None and f_pas is not None:
            titulo = (f"Mulheres são {pct(f_cond, 0)} de quem dirigia, mas {pct(f_pas, 0)} "
                      f"de quem estava de carona")
        else:
            titulo = "Participação de cada sexo por papel na ocorrência"
        UI.grafico(G.barras_100(part, cont, {s: C.COR[s] for s in C.SEXOS}, titulo,
                                "% de cada papel · só envolvidos com sexo informado",
                                altura=110 + 48 * len(part)), cont, "c3_papel")

    c1, c2 = st.columns(2)
    # ---------- Idade ----------
    with c1:
        idade = A.distribuicao_idade(cond)
        if len(idade) and set(C.SEXOS) <= set(idade.columns):
            med = cond.groupby("sexo", observed=True)["idade"].median()
            titulo = (f"Condutoras são um pouco mais jovens: mediana de {n(med['Feminino'])} anos "
                      f"contra {n(med['Masculino'])}")
            UI.grafico(G.linhas_sexo(idade.rolling(3, center=True, min_periods=1).mean(), titulo,
                                     "% dos condutores de cada sexo por idade (média móvel de 3 anos) · 14 a 90 anos",
                                     "Idade", "% dos condutores"), idade.round(2), "c3_idade")
            UI.nota(f"{n(int(ev['idade_padrao_condutor'].sum()))} condutores com idade 0 no dado original foram "
                    "tratados como idade não informada: é um valor padrão de preenchimento, não idade real.")
    # ---------- Veículo ----------
    with c2:
        t, p = A.pct_por_sexo(cond, "grupo_veiculo", ordem=C.ORDEM_VEICULO[:-1])
        if len(p) and set(C.SEXOS) <= set(p.columns):
            auto_f = p.loc["Automóvel", "Feminino"] if "Automóvel" in p.index else 0
            cam_m = p.loc["Caminhão", "Masculino"] if "Caminhão" in p.index else 0
            cam_f = p.loc["Caminhão", "Feminino"] if "Caminhão" in p.index else 0
            titulo = (f"Elas dirigiam sobretudo automóveis ({pct(auto_f, 0)}); "
                      f"caminhões são {pct(cam_m, 0)} dos casos deles e {pct(cam_f, 0)} dos delas")
            UI.grafico(G.barras_sexo(p, titulo, "% dos condutores de cada sexo por tipo de veículo",
                                     "% dos condutores", hover_n=t), t, "c3_veic")

    # ---------- Gravidade por papel ----------
    t, p = A.estado_por(ev, "tipo_envolvido", ["Condutor", "Passageiro", "Pedestre", "Cavaleiro"])
    if len(p):
        pior = p["Óbito"].idxmax() if "Óbito" in p else ""
        titulo = (f"Pedestres são o grupo mais vulnerável: {pct(p.loc['Pedestre', 'Óbito'])} morrem"
                  if "Pedestre" in p.index else "Estado físico após o acidente no recorte")
        UI.grafico(G.barras_100(p, t, C.COR_ESTADO, titulo,
                                "Estado físico após o acidente, % de cada papel · só estado informado",
                                altura=110 + 48 * len(p)), t, "c3_estado")

    # ---------- Ponte para o KM 4 ----------
    comp = A.gravidade_todos_vs_condutores(ev)
    if len(comp) == 4:
        tab = comp.pivot(index="grupo", columns="sexo", values="letalidade")
        tab = tab.reindex(["Todos os envolvidos", "Somente condutores"])
        UI.grafico(G.barras_sexo(tab, "Filtrar só quem dirigia muda o tamanho da diferença",
                                 "Taxa de letalidade por sexo · todos os envolvidos vs. somente condutores",
                                 "% que morreram", altura=280), tab.round(2), "c3_ponte")
        UI.leitura(
            f"Entre todos os envolvidos, a letalidade é de {pct(tab.iloc[0]['Feminino'], 2)} para mulheres e "
            f"{pct(tab.iloc[0]['Masculino'], 2)} para homens. Entre os <b>condutores</b>, passa a "
            f"{pct(tab.iloc[1]['Feminino'], 2)} e {pct(tab.iloc[1]['Masculino'], 2)}. A diferença muda porque as "
            f"mulheres aparecem muito mais como passageiras, um papel com risco próprio. Misturar papéis "
            f"misturaria quem dirigia com quem estava de carona.")
    f_c = part.loc["Condutor", "Feminino"] if "Condutor" in part.index and "Feminino" in part.columns else None
    f_p = part.loc["Passageiro", "Feminino"] if "Passageiro" in part.index and "Feminino" in part.columns else None
    if f_c is None or f_p is None or not (f_c < 50 < f_p) or ctx.filtros.sexos:
        UI.nota("A descoberta deste capítulo compara os dois sexos em todos os papéis. Para vê-la, "
                "retire os filtros de sexo e de tipo de envolvido.")
        return
    UI.descoberta(
        "As mulheres são <b>minoria entre quem dirigia</b> e maioria entre passageiros. Também dirigiam "
        "<b>outros veículos</b>: mais automóveis, quase nenhum caminhão. Esses dois fatos obrigam o próximo "
        "passo a comparar só condutores e a <b>controlar o tipo de veículo</b>; do contrário, estaríamos "
        "comparando um carro de passeio com uma carreta.")
