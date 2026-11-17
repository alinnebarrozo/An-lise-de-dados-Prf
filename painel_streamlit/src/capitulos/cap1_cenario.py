"""KM 1 — O cenário: a dimensão do problema."""
import streamlit as st

from .. import analises as A
from .. import componentes as UI
from .. import config as C
from .. import graficos as G
from .. import metricas as M
from ..formatos import n, pct, pp


def _delta(a, b, taxa=False, casas=1):
    if taxa:
        return pp(b - a, casas)
    return ("+" if b >= a else "−") + pct(abs(100 * (b - a) / a), 1) if a else "—"


def render(ctx) -> None:
    oc, ev = ctx.oc, ctx.ev
    UI.marco("KM 1", "O cenário",
             "Qual é o tamanho do problema nas rodovias federais?",
             "Antes de comparar homens e mulheres, é preciso saber de que volume estamos falando "
             "e se ele muda com o tempo. Aqui separamos três grãos que não podem ser misturados: "
             "<b>ocorrências</b> (acidentes), <b>envolvidos</b> (pessoas) e <b>óbitos</b>.")
    if oc.empty or ev.empty:
        UI.sem_dados()
        return

    k = M.kpis(oc, ev)
    UI.kpis([
        {"rot": "Ocorrências", "val": n(k["ocorrencias"]), "sub": "acidentes registrados pela PRF"},
        {"rot": "Pessoas envolvidas", "val": n(k["envolvidos"]),
         "sub": f"{n(k['envolvidos'] / k['ocorrencias'], 1)} por ocorrência"},
        {"rot": "Óbitos", "val": n(k["obitos"]), "sub": "envolvidos com estado = óbito"},
        {"rot": "Ocorrências com morte", "val": pct(k["pct_ocorrencias_fatais"]),
         "sub": f"1 a cada {n(100 / k['pct_ocorrencias_fatais'], 0)} acidentes" if k["pct_ocorrencias_fatais"] else ""},
        {"rot": "Taxa de letalidade", "val": pct(k["letalidade"], 2),
         "sub": "óbitos ÷ envolvidos com estado informado"},
        {"rot": "Índice de gravidade", "val": pct(k["gravidade"]),
         "sub": "(óbitos + lesões graves) ÷ estado informado"},
    ])
    UI.nota("Óbitos são contados na base de pessoas. A soma de mortos por ocorrência confere com ela "
            "(diferença zero no diagnóstico do ETL).")

    # ---------- Comparação entre períodos ----------
    anos = sorted(oc["ano"].unique().tolist())
    if len(anos) >= 2:
        with st.container(border=True):
            st.markdown("**Comparar períodos na mesma janela de meses**")
            c1, c2, _ = st.columns([1, 1, 2])
            ano_a = c1.selectbox("Ano base", anos, index=len(anos) - 2, key="cmp_a")
            ano_b = c2.selectbox("Comparar com", anos, index=len(anos) - 1, key="cmp_b")
            if ano_a != ano_b:
                ka, kb, meses = A.comparar_anos(oc, ev, ano_a, ano_b)
                if meses and ka["ocorrencias"] and kb["ocorrencias"]:
                    janela = f"{C.MESES[meses[0] - 1]}–{C.MESES[meses[-1] - 1]}"
                    UI.kpis([
                        {"rot": f"Ocorrências ({janela})", "val": n(kb["ocorrencias"]),
                         "sub": f"{ano_a}: {n(ka['ocorrencias'])}",
                         "delta": _delta(ka["ocorrencias"], kb["ocorrencias"]) + f" vs {ano_a}"},
                        {"rot": f"Óbitos ({janela})", "val": n(kb["obitos"]),
                         "sub": f"{ano_a}: {n(ka['obitos'])}",
                         "delta": _delta(ka["obitos"], kb["obitos"]) + f" vs {ano_a}"},
                        {"rot": "Ocorrências com morte", "val": pct(kb["pct_ocorrencias_fatais"]),
                         "sub": f"{ano_a}: {pct(ka['pct_ocorrencias_fatais'])}",
                         "delta": _delta(ka["pct_ocorrencias_fatais"], kb["pct_ocorrencias_fatais"], True, 2)},
                        {"rot": "Taxa de letalidade", "val": pct(kb["letalidade"], 2),
                         "sub": f"{ano_a}: {pct(ka['letalidade'], 2)}",
                         "delta": _delta(ka["letalidade"], kb["letalidade"], True, 2)},
                    ])
                    UI.nota(f"Os dois anos usam só os meses presentes em ambos ({janela}). "
                            "Isso evita comparar 2026, que vai até agosto, com um ano inteiro.")
                else:
                    UI.nota("Os anos escolhidos não têm meses em comum no recorte atual.")

    # ---------- Evolução ----------
    mensal = A.mensal(oc, ev)
    media = mensal["ocorrencias"].mean()
    pico = mensal.loc[mensal["ocorrencias"].idxmax()]
    cv = 100 * mensal["ocorrencias"].std() / media if len(mensal) > 1 else 0
    titulo = ("O volume mensal é estável: oscila pouco em torno da média"
              if cv < 12 else "O volume mensal varia bastante ao longo do período")
    UI.grafico(G.evolucao_mensal(
        mensal, titulo,
        f"Média de {n(media)} ocorrências por mês · pico em {C.MESES[int(pico['mes']) - 1]}/{int(pico['ano'])} "
        f"({n(pico['ocorrencias'])}) · variação típica de {pct(cv, 0)} em torno da média"),
        mensal[["mes_ref", "ocorrencias", "obitos"]].rename(
            columns={"mes_ref": "mês", "ocorrencias": "ocorrências", "obitos": "óbitos"}), "c1_mensal")

    # ---------- Gravidade por ano ----------
    cont, pcts = A.classificacao_por_ano(oc)
    fatal = pcts["Com Vítimas Fatais"] if "Com Vítimas Fatais" in pcts else None
    if fatal is not None and len(fatal) > 1:
        amplitude = fatal.max() - fatal.min()
        titulo = ("A proporção de acidentes fatais quase não muda de um ano para outro"
                  if amplitude < 1 else "A proporção de acidentes fatais muda entre os anos")
        sub = f"% das ocorrências de cada ano · fatais entre {pct(fatal.min())} e {pct(fatal.max())}"
    else:
        titulo, sub = "Como as ocorrências se dividem por gravidade", "% das ocorrências"
    pcts.index = pcts.index.astype(str)
    cont.index = cont.index.astype(str)
    UI.grafico(G.barras_100(pcts, cont, C.COR_CLASSIFICACAO, titulo, sub,
                            altura=120 + 46 * len(pcts)), cont, "c1_classif")

    # ---------- Narrativa ----------
    feridas = 100 * (oc["classificacao_acidente"] == "Com Vítimas Feridas").mean()
    UI.leitura(
        f"No recorte há <b>{n(k['ocorrencias'])} acidentes</b>, com <b>{n(k['envolvidos'])} pessoas</b> e "
        f"<b>{n(k['obitos'])} mortes</b>. A maior parte dos acidentes deixa feridos ({pct(feridas)}), e "
        f"<b>{pct(k['pct_ocorrencias_fatais'])}</b> terminam com pelo menos uma morte. Entre as pessoas com "
        f"estado físico informado, {pct(k['letalidade'], 2)} morreram e {pct(k['gravidade'])} morreram ou "
        f"tiveram lesões graves. Como 2026 é parcial, os anos devem ser comparados por taxas ou na mesma "
        f"janela de meses, nunca pelos totais.")
    kpa = A.kpis_por_ano(oc, ev)
    estavel = len(kpa) < 2 or (kpa["pct_ocorrencias_fatais"].max() - kpa["pct_ocorrencias_fatais"].min()) < 1
    if not estavel:
        UI.descoberta(
            f"Cerca de 1 em cada {n(100 / k['pct_ocorrencias_fatais'], 0)} acidentes mata alguém, mas essa proporção "
            f"<b>muda entre os anos</b> neste recorte: vale investigar o que mudou. "
            f"A pergunta seguinte é “onde, quando e com quem”.")
        return
    UI.descoberta(
        f"O problema é grande e <b>estável</b>: cerca de 1 em cada {n(100 / k['pct_ocorrencias_fatais'], 0)} "
        f"acidentes mata alguém, e essa proporção praticamente não muda ao longo do período. "
        f"A pergunta deixa de ser “quanto” e passa a ser “onde, quando e com quem”.")
