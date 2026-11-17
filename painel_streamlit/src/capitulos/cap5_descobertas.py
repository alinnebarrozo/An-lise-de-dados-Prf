"""KM 5 — Descobertas, hipóteses, limitações e próximos passos."""
import pandas as pd
import streamlit as st

from .. import componentes as UI
from ..formatos import n, pct, vezes


def render(ctx) -> None:
    h = ctx.extra["hipoteses"]
    v = h["veredito"]
    ev_all, oc_all = ctx.base.envolvidos, ctx.base.ocorrencias
    sem_sexo = 100 * ev_all["sexo"].isna().mean()
    sem_estado = 100 * ev_all["estado_fisico"].isna().mean()
    fatais = 100 * oc_all["fatal"].mean()
    UI.marco("KM 5", "Descobertas",
             "Afinal, o ditado se sustenta?",
             "Os veredictos abaixo usam a <b>base completa</b> (jan/2024 a ago/2026), independente dos filtros, "
             "e seguem regras fixas: uma hipótese só é confirmada ou rejeitada quando os intervalos de confiança "
             "não se sobrepõem. Se os dados forem atualizados, os veredictos são recalculados.")

    UI.kpis([
        {"rot": "Mulheres entre os condutores", "val": pct(h["share_f_condutores"]),
         "sub": f"de {n(h['n_condutores'])} condutores com sexo informado"},
        {"rot": "Letalidade · condutoras", "val": pct(h["let_f"], 2),
         "sub": f"IC 95%: {pct(h['let_f_ic'][0], 2)} a {pct(h['let_f_ic'][1], 2)}"},
        {"rot": "Letalidade · condutores", "val": pct(h["let_m"], 2),
         "sub": f"IC 95%: {pct(h['let_m_ic'][0], 2)} a {pct(h['let_m_ic'][1], 2)}"},
        {"rot": "Chance de óbito H ÷ M, ajustada", "val": vezes(h["or_ajustada"]["or"], 2),
         "sub": f"sem ajuste: {vezes(h['or_bruta']['or'], 2)}"},
    ])

    st.markdown("#### Hipóteses testadas")
    te, tc, oa = h["teste_estado"], h["teste_causa"], h["or_ajustada"]
    c1, c2 = st.columns(2)
    with c1:
        UI.hipotese(
            "H1", "Mulheres se envolvem em mais acidentes", v["H1"],
            f"As mulheres são só {pct(h['share_f_condutores'])} dos condutores envolvidos. Isso <b>não</b> é taxa "
            "de risco: a base não informa quantas mulheres dirigem nem quantos km rodam. Sem esse denominador, "
            "não dá para dizer quem se acidenta mais <i>por km dirigido</i>.",
            "Evidência: participação nos registros · falta o dado de exposição (habilitados, frota, km)")
    with c2:
        UI.hipotese(
            "H2", "Acidentes com condutoras são mais graves", v["H2"],
            (f"É o contrário: a letalidade das condutoras ({pct(h['let_f'], 2)}) é menor que a dos condutores "
             f"({pct(h['let_m'], 2)}), e os intervalos de confiança não se sobrepõem. O índice de gravidade segue a "
             f"mesma direção ({pct(h['grav_f'])} vs. {pct(h['grav_m'])}).") if v["H2"] == "nao_confirmada" else
            (f"Letalidade das condutoras: {pct(h['let_f'], 2)}; dos condutores: {pct(h['let_m'], 2)}. "
             "Veredicto definido pela comparação dos intervalos de confiança de 95%."),
            f"Evidência: χ² = {n(te['qui2'])}, p < 0,001 · V de Cramér = {n(te['v'], 3)} (efeito {te['efeito']})"
            if te else "Evidência: taxas com IC 95%")
    c3, c4 = st.columns(2)
    with c3:
        UI.hipotese(
            "H3", "O perfil de causas é diferente entre os sexos", v["H3"],
            "Em acidentes com um único veículo, falhas de reação aparecem mais entre mulheres; álcool, velocidade "
            "e sono aparecem mais entre homens. A diferença é estatisticamente clara, mas de <b>efeito "
            f"{tc['efeito'] if tc else '—'}</b>: os perfis se parecem mais do que diferem.",
            f"Evidência: χ² = {n(tc['qui2'])}, gl = {tc['gl']}, V de Cramér = {n(tc['v'], 3)} · "
            f"n = {n(tc['n'])} condutores em acidentes de veículo único" if tc else "Evidência: insuficiente")
    with c4:
        UI.hipotese(
            "H4", "A diferença de letalidade persiste com controles", v["H4"],
            f"Em {h['estratos_m_maior']} de {h['estratos_validos']} tipos de veículo com dados suficientes, a "
            f"letalidade dos homens é maior"
            + ("" if not h["excecoes"] else
               " (exceção: " + ", ".join(f"{g.lower()}, com só {n(nf)} condutoras e IC amplo" for g, nf in h["excecoes"]) + ")")
            + f". Na regressão logística, a razão de chances cai de "
            f"{n(h['or_bruta']['or'], 2)} para {n(oa['or'], 2)}: parte da diferença vinha do veículo, da idade e do "
            "horário, mas não toda.",
            f"Evidência: OR ajustada = {n(oa['or'], 2)} (IC 95%: {n(oa['ic_inf'], 2)} a {n(oa['ic_sup'], 2)}) · "
            "ajustada por veículo, idade, fase do dia, trecho e dia")

    st.markdown("#### O que aprendemos")
    UI.leitura(
        "<ol style='margin:0;padding-left:20px'>"
        f"<li><b>O problema é estável.</b> Cerca de {pct(fatais, 0)} das ocorrências têm morte, ano após ano (KM 1).</li>"
        "<li><b>Volume e letalidade apontam para lugares diferentes.</b> Os acidentes se concentram nos grandes "
        "corredores e no horário de pico, mas os que matam se concentram à noite e de madrugada (KM 2).</li>"
        f"<li><b>Mulheres são minoria ao volante e maioria na carona.</b> São {pct(h['share_f_condutores'], 0)} "
        f"dos condutores e {pct(h['share_f_passageiros'], 0)} dos passageiros, e dirigiam outros tipos de veículo (KM 3).</li>"
        "<li><b>Os dados não sustentam o ditado.</b> Quando dirigem, mulheres têm acidentes de menor letalidade, "
        "mesmo comparando o mesmo tipo de veículo, idade e horário (KM 4).</li>"
        "<li><b>O sexo pesa pouco.</b> Veículo (moto, bicicleta), madrugada, trecho rural e idade 60+ "
        "explicam muito mais da gravidade (KM 4).</li></ol>",
        "Principais descobertas")

    c5, c6 = st.columns(2)
    with c5:
        UI.leitura(
            "<ul style='margin:0;padding-left:18px'>"
            "<li><b>Sem exposição:</b> não há km rodados nem número de condutores por sexo. Nenhum indicador aqui "
            "é risco por motorista.</li>"
            "<li><b>Só quem se acidentou:</b> a base condiciona ao acidente. Comparações de gravidade valem "
            "<i>dado que houve acidente</i>.</li>"
            "<li><b>Causa é da ocorrência:</b> por isso a análise de causas prioriza acidentes de veículo único.</li>"
            "<li><b>Associação, não causa:</b> velocidade, cinto/capacete e estado do veículo não estão na base.</li>"
            f"<li><b>Ausentes:</b> {pct(sem_sexo)} dos envolvidos sem sexo e {pct(sem_estado)} sem estado físico "
            "ficam fora dos percentuais.</li>"
            "<li><b>2026 parcial:</b> só até agosto; comparar pela mesma janela de meses.</li></ul>",
            "Limitações")
    with c6:
        UI.leitura(
            "<ul style='margin:0;padding-left:18px'>"
            "<li><b>Normalizar por exposição:</b> cruzar com habilitados por sexo e UF (Senatran) para estimar "
            "taxa por condutor.</li>"
            "<li><b>Todas as causas:</b> usar a base <code>todas_causas_tipos</code>, que hoje entra só como "
            "contagem, para analisar combinações de causas.</li>"
            "<li><b>Modelos por veículo:</b> ajustar modelos separados para motos e automóveis, onde há mais mulheres.</li>"
            "<li><b>Série histórica:</b> incluir anos anteriores a 2024 para testar tendência.</li>"
            "<li><b>Interação:</b> testar se o efeito do sexo muda com a idade (jovens vs. 60+).</li></ul>",
            "Próximas investigações")

    with st.expander("Registro de qualidade dos dados (ETL + painel)"):
        q = ctx.base.qualidade.copy()
        extra = pd.DataFrame([{
            "base": "pessoas", "verificação": "Condutor com idade 0 (valor padrão de preenchimento)",
            "registros_afetados": int(ctx.base.envolvidos["idade_padrao_condutor"].sum()),
            "tratamento": "Painel: idade tratada como não informada nas análises de idade"}])
        st.dataframe(pd.concat([q, extra], ignore_index=True), use_container_width=True, hide_index=True)
    with st.expander("Dicionário de indicadores"):
        st.dataframe(ctx.base.kpis, use_container_width=True, hide_index=True)

    UI.descoberta(
        "<b>Resposta à pergunta do título:</b> nos acidentes das rodovias federais, ter uma mulher ao volante "
        "está associado a <b>menor</b> letalidade, não maior. O que a base não responde é se as mulheres se "
        "acidentam mais ou menos <i>por km dirigido</i>. Para isso falta o dado de exposição. "
        "A crença popular não encontra apoio nos dados disponíveis.")
