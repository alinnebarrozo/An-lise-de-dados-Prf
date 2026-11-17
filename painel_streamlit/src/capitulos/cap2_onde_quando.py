"""KM 2 — Onde e quando os acidentes acontecem."""
import streamlit as st

from .. import analises as A
from .. import componentes as UI
from .. import config as C
from .. import graficos as G
from ..formatos import n, pct


def render(ctx) -> None:
    oc = ctx.oc
    UI.marco("KM 2", "Onde e quando",
             "Os acidentes se concentram em lugares e horários específicos?",
             "Campanhas e fiscalização têm alcance limitado. Saber onde e quando o risco se concentra "
             "indica onde agir primeiro. Aqui separamos <b>volume</b> (quantos acidentes) de "
             "<b>letalidade</b> (que parte deles mata), porque os dois nem sempre apontam o mesmo lugar.")
    if oc.empty:
        UI.sem_dados()
        return

    metrica = st.segmented_control(
        "Ver rankings e calendário por", ["Volume de ocorrências", "% de ocorrências com morte"],
        default="Volume de ocorrências", key="c2_metrica") or "Volume de ocorrências"
    por_volume = metrica.startswith("Volume")
    chave = "ocorrencias" if por_volume else "pct"

    # ---------- Mapa + UF ----------
    col_mapa, col_uf = st.columns([1.55, 1])
    with col_mapa:
        pontos = A.pontos_mapa(oc)
        top = pontos.nlargest(1, "ocorrencias")
        sub = ("Cada círculo agrega uma área de ~25 km · tamanho = ocorrências · cor = % com morte"
               + (f" · maior concentração: {top['local'].iat[0]}" if len(top) else ""))
        if len(pontos) >= 10:
            ordenado = pontos["ocorrencias"].sort_values(ascending=False)
            k10 = max(1, int(round(len(ordenado) * 0.10)))
            conc = 100 * ordenado.head(k10).sum() / ordenado.sum()
            titulo_mapa = f"10% das áreas concentram {pct(conc, 0)} dos acidentes"
        else:
            titulo_mapa = "Onde ficam os acidentes do recorte"
        UI.grafico(G.mapa_pontos(pontos, titulo_mapa, sub),
                   chave="c2_mapa")
    with col_uf:
        uf = A.ranking_local(oc, "uf", chave, top=12, minimo=200)
        if por_volume and len(uf) <= 3:
            titulo, sub = "Ocorrências por UF no recorte", "Ocorrências por UF"
        elif por_volume:
            top3 = 100 * uf.head(3).sum() / len(oc)
            titulo = f"Três UFs somam {pct(top3, 0)} dos acidentes"
            sub = "Ocorrências por UF · 12 maiores"
        else:
            titulo = f"{uf.index[0]} tem a maior proporção de acidentes fatais" if len(uf) else "UFs"
            sub = "% das ocorrências com morte · UFs com 200+ ocorrências"
        UI.grafico(G.ranking(uf, titulo, sub, destaque=3, formato="n" if por_volume else "pct",
                             altura=560), uf.rename("valor").to_frame(), "c2_uf")
    UI.nota("O volume acompanha o tamanho da malha e da frota de cada estado. Sem dado de exposição "
            "(km rodados), o ranking por volume não mede risco.")

    # ---------- Rodovias e municípios ----------
    c1, c2 = st.columns(2)
    with c1:
        br = A.ranking_local(oc, "br", chave, top=10, minimo=200)
        if por_volume and len(br):
            folga = len(br) > 2 and br.iat[1] >= 1.5 * br.iat[2]
            t = (f"{br.index[0]} e {br.index[1]} lideram" + (" com folga" if folga else "")) if len(br) > 1 \
                else f"{br.index[0]} lidera"
            s = f"Ocorrências por rodovia · {br.index[0]} concentra {pct(100 * br.iat[0] / len(oc))} do recorte"
        else:
            t = "Rodovias com menos volume podem ser as mais letais"
            s = "% das ocorrências com morte · rodovias com 200+ ocorrências"
        UI.grafico(G.ranking(br, t, s, destaque=2, formato="n" if por_volume else "pct"),
                   br.rename("valor").to_frame(), "c2_br")
    with c2:
        mu = A.ranking_local(oc, "municipio", chave, top=10, minimo=200)
        if por_volume and len(mu):
            t = f"{mu.index[0]} lidera, com {n(mu.iat[0])} ocorrências"
        else:
            t = "Municípios onde os acidentes mais matam" if len(mu) else "Sem municípios com 200+ ocorrências"
        s = "Ocorrências por município" if por_volume else "% com morte · municípios com 200+ ocorrências"
        UI.grafico(G.ranking(mu, t, s, destaque=3, formato="n" if por_volume else "pct"),
                   mu.rename("valor").to_frame(), "c2_mun")

    # ---------- Calendário ----------
    calor = A.calor_dia_hora(oc, "ocorrencias" if por_volume else "pct")
    if por_volume:
        pico = calor.stack().idxmax()
        madrugada = calor.loc[:, [h for h in calor.columns if h <= 5]].to_numpy().mean()
        calma = madrugada < 0.5 * calor.to_numpy().mean()
        titulo = (f"O pico de acidentes é {C.DIA_FRASE.get(pico[0], pico[0])}, às {pico[1]}h"
                  + ("; as madrugadas têm pouco movimento" if calma else ""))
        sub = "Ocorrências por dia da semana e hora de início"
        rot, fmt = "ocorrências", ",.0f"
    else:
        noite = calor.loc[:, [h for h in calor.columns if h <= 5]].mean().mean()
        dia = calor.loc[:, [h for h in calor.columns if 9 <= h <= 16]].mean().mean()
        titulo = f"De madrugada há menos acidentes, mas eles matam {n(noite / dia, 1)}× mais"
        sub = "% das ocorrências com morte por dia e hora (0h–5h vs 9h–16h)"
        rot, fmt = "% com morte", ".1f"
    UI.grafico(G.mapa_calor(calor, titulo, sub, rot, fmt), calor.round(1), "c2_calor")

    c3, c4 = st.columns(2)
    with c3:
        fase = A.por_fase(oc)
        if len(fase) and fase["ocorrencias"].min() >= 100 and fase["pct_fatais"].min() > 0:
            noite = fase.set_index("fase_dia")
            razao = noite["pct_fatais"].max() / noite["pct_fatais"].min()
            pior = noite["pct_fatais"].idxmax()
            fig = G.barras_simples(
                fase["fase_dia"].astype(str), fase["pct_fatais"],
                (f"Acidentes à noite e ao amanhecer matam até {n(razao, 1)}× mais que os de pleno dia"
                 if pior in ("Plena Noite", "Amanhecer") else
                 f"A proporção de acidentes com morte varia até {n(razao, 1)}× entre as fases do dia"),
                f"% das ocorrências com morte por fase do dia · maior em: {pior}",
                "% com morte", "%{x}: <b>%{y:.1f}%</b> com morte",
                destaque_idx=[i for i, f in enumerate(fase["fase_dia"].astype(str))
                              if f in ("Plena Noite", "Amanhecer")],
                formato_texto=[pct(v) for v in fase["pct_fatais"]])
            fig.update_yaxes(ticksuffix="%")
            UI.grafico(fig, fase.round(2), "c2_fase")
        elif len(fase):
            UI.nota("Poucas ocorrências por fase do dia neste recorte para comparar a letalidade com segurança.")
    with c4:
        saz, completos = A.sazonalidade(oc)
        if len(saz):
            maior = saz.loc[saz["media"].idxmax()]
            menor = saz.loc[saz["media"].idxmin()]
            fig = G.barras_simples(
                [C.MESES[m - 1] for m in saz["mes"]], saz["media"],
                f"{C.MESES_LONGO[int(maior['mes']) - 1].capitalize()} é o mês mais carregado; "
                f"{C.MESES_LONGO[int(menor['mes']) - 1]}, o mais leve",
                f"Média de ocorrências por mês · anos completos no recorte: {', '.join(map(str, completos))}",
                "ocorrências/mês", "%{x}: <b>%{y:,.0f}</b> em média",
                destaque_idx=[int(maior["mes"]) - 1])
            UI.grafico(fig, saz.round(0), "c2_saz")
        else:
            UI.nota("A sazonalidade usa apenas anos completos. O recorte atual não tem nenhum ano com 12 meses.")

    # ---------- Narrativa ----------
    fase = A.por_fase(oc).set_index("fase_dia")
    if {"Pleno dia", "Plena Noite"} <= set(fase.index.astype(str)) \
            and fase.loc["Plena Noite", "pct_fatais"] > fase.loc["Pleno dia", "pct_fatais"] \
            and fase.loc["Plena Noite", "ocorrencias"] >= 100:
        dia, noite = fase.loc["Pleno dia"], fase.loc["Plena Noite"]
        UI.leitura(
            f"O volume se concentra nos estados e rodovias de maior tráfego e cresce nos fins de tarde e "
            f"fins de semana. Já a <b>letalidade</b> segue outra lógica: à noite acontecem "
            f"{pct(noite['pct_ocorrencias'], 0)} dos acidentes, mas {pct(noite['pct_fatais'])} deles têm morte, "
            f"contra {pct(dia['pct_fatais'])} durante o dia. Menos movimento, menos visibilidade e mais velocidade "
            f"são explicações plausíveis, mas não estão medidas nesta base.")
        UI.descoberta(
            "<b>Onde e quando há mais acidentes não é onde e quando eles mais matam.</b> O volume aponta para os "
            "grandes corredores e o horário de pico; a letalidade aponta para a noite e a madrugada. "
            "Isso será decisivo no KM 4: se homens e mulheres dirigem em horários diferentes, parte da diferença "
            "de gravidade pode vir do horário, e não do sexo.")
