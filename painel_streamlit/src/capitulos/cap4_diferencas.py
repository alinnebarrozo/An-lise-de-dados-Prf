"""KM 4 — Investigando as diferenças entre condutoras e condutores."""
import streamlit as st

from .. import analises as A
from .. import componentes as UI
from .. import config as C
from .. import graficos as G
from .. import metricas as M
from ..formatos import n, pct, vezes

ESTRATOS = {
    "Tipo de veículo": "grupo_veiculo",
    "Faixa etária": "faixa_etaria",
    "Fase do dia": "fase_dia",
    "Trecho urbano/rural": "uso_solo",
}

CARACTERISTICAS = {
    "Tipo de acidente": ("tipo_acidente", None, 8),
    "Fase do dia": ("fase_dia", C.ORDEM_FASE, None),
    "Dia da semana": ("dia_semana", C.ORDEM_DIA, None),
    "Condição meteorológica": ("condicao_metereologica", None, 6),
    "Traçado da via": ("tracado_via", None, 6),
    "Tipo de pista": ("tipo_pista", None, None),
}


def render(ctx) -> None:
    UI.marco("KM 4", "Investigando as diferenças",
             "A diferença entre condutoras e condutores se sustenta quando olhamos de perto?",
             "Aqui a comparação é feita só entre <b>condutores</b> com sexo informado. Todo percentual usa como "
             "denominador os condutores de cada sexo. Isso não é taxa de risco: a base não diz quantos homens e "
             "mulheres dirigem nem quanto. Cada diferença vem com intervalo de confiança de 95% e com uma medida de "
             "<b>tamanho do efeito</b>, porque, com centenas de milhares de registros, quase tudo dá “significativo”. "
             + UI.legenda_sexo())

    f = ctx.filtros.sem("sexos", "tipos_envolvido").com(tipos_envolvido=("Condutor",))
    _, ev = ctx.recorte(f)
    cond = M.condutores_com_sexo(ev)
    avisos = []
    if ctx.filtros.sexos:
        avisos.append("o filtro de sexo não se aplica aqui: este capítulo compara os dois")
    if ctx.filtros.tipos_envolvido and set(ctx.filtros.tipos_envolvido) != {"Condutor"}:
        avisos.append("aqui o tipo de envolvido é sempre Condutor")
    if avisos:
        UI.nota("Neste capítulo, " + "; ".join(avisos) + ".")
    if cond.empty or cond["sexo"].nunique() < 2:
        UI.sem_dados()
        return

    # ---------- Comparação central ----------
    res = A.resumo_sexo(cond)
    tx = res["taxas"]
    tab, teste = A.teste_sexo_estado(cond)
    fem, mas = tx.loc["Feminino"], tx.loc["Masculino"]
    rr = res.get("rr_obito")
    UI.kpis([
        {"rot": "Letalidade · condutoras", "val": pct(fem["letalidade"], 2),
         "sub": f"IC 95%: {pct(fem['let_ic_inf'], 2)} a {pct(fem['let_ic_sup'], 2)} · n = {n(fem['n'])}"},
        {"rot": "Letalidade · condutores", "val": pct(mas["letalidade"], 2),
         "sub": f"IC 95%: {pct(mas['let_ic_inf'], 2)} a {pct(mas['let_ic_sup'], 2)} · n = {n(mas['n'])}"},
        {"rot": "Risco relativo de óbito (H ÷ M)", "val": vezes(rr["rr"], 2) if rr else "—",
         "sub": f"IC 95%: {n(rr['ic_inf'], 2)} a {n(rr['ic_sup'], 2)}" if rr else "sem óbitos femininos no recorte"},
        {"rot": "Força da associação sexo × estado físico",
         "val": n(teste["v"], 3) if teste else "—",
         "sub": f"V de Cramér · efeito {teste['efeito']}" + (" · p < 0,001" if teste and teste["p"] < 0.001 else "")
                if teste else ""},
    ])

    _, p = M.composicao(cond[cond["estado_informado"]], "sexo", "estado_fisico", C.ORDEM_ESTADO)
    p.index = p.index.astype(str)
    t2 = tab.copy()
    t2.index = t2.index.astype(str)
    titulo = ("Condutoras saem ilesas com menos frequência, mas morrem com menos frequência"
              if p.loc["Feminino", "Ileso"] < p.loc["Masculino", "Ileso"]
              and p.loc["Feminino", "Óbito"] < p.loc["Masculino", "Óbito"]
              else "Estado físico após o acidente, por sexo do condutor")
    UI.grafico(G.barras_100(p.reindex(C.SEXOS), t2.reindex(C.SEXOS), C.COR_ESTADO, titulo,
                            "% dos condutores de cada sexo com estado físico informado", altura=230),
               t2, "c4_estado")

    # ---------- Estratificação ----------
    st.markdown("#### A diferença persiste dentro de grupos comparáveis?")
    UI.nota("Se a diferença viesse só do veículo, da idade ou do horário, ela desapareceria dentro de cada grupo. "
            "Escolha a variável de controle e a medida.")
    c1, c2 = st.columns([2, 1])
    estrato = c1.segmented_control("Controlar por", list(ESTRATOS), default="Tipo de veículo",
                                   key="c4_estrato") or "Tipo de veículo"
    medida_rot = c2.segmented_control("Medida", ["Letalidade", "Índice de gravidade"], default="Letalidade",
                                      key="c4_medida") or "Letalidade"
    coluna = ESTRATOS[estrato]
    medida = "letalidade" if medida_rot == "Letalidade" else "gravidade"
    base_estr = cond.copy()
    if coluna == "uso_solo":
        base_estr["uso_solo"] = base_estr["uso_solo"].astype("string").map({"Sim": "Urbano", "Não": "Rural"})
    if coluna == "grupo_veiculo":
        base_estr = base_estr[base_estr["grupo_veiculo"] != "Outros"]
    estr = M.taxas_por(base_estr, [coluna, "sexo"])
    if coluna == "uso_solo":
        estr[coluna] = estr[coluna].astype("category")
    piv = estr.pivot_table(index=coluna, columns="sexo", values=[medida, "n"], observed=True)
    validos = piv[(piv[("n", "Feminino")] >= 100) & (piv[("n", "Masculino")] >= 100)]
    m_maior = int((validos[(medida, "Masculino")] > validos[(medida, "Feminino")]).sum())
    titulo = (f"Em {m_maior} de {len(validos)} grupos com dados suficientes, a {medida_rot.lower()} "
              f"dos homens é maior")
    UI.grafico(G.taxa_com_ic(estr, coluna, medida, titulo,
                             f"{medida_rot} por {estrato.lower()} e sexo · barras = IC 95% · "
                             "círculo vazado = menos de 100 condutores (evidência fraca)",
                             f"{medida_rot} (%)"),
               estr[[coluna, "sexo", "n", medida]].round(2), "c4_estrato_fig")

    # ---------- Modelo ajustado ----------
    reg = ctx.extra.get("regressao")
    if reg is not None:
        lin = reg[reg["termo"] == "sexo=Masculino"].iloc[0]
        bruta = ctx.extra.get("or_bruta")
        st.markdown("#### Controlando tudo ao mesmo tempo: regressão logística")
        UI.grafico(G.floresta(
            reg,
            f"Mesmo com os controles, a chance de óbito de um condutor homem é {n(lin['or'], 2)}× a de uma condutora",
            f"Desfecho: óbito · ajustado por veículo, faixa etária, fase do dia, trecho urbano/rural e dia da semana · "
            f"n = {n(reg.attrs['n'])} condutores, {n(reg.attrs['eventos'])} óbitos · base completa"),
            reg.drop(columns=["coef", "ep"]).round(4), "c4_floresta")
        UI.leitura(
            f"Sem ajuste, a razão de chances de óbito (homens ÷ mulheres) é <b>{n(bruta['or'], 2)}</b>. "
            f"Com ajuste, cai para <b>{n(lin['or'], 2)}</b> (IC 95%: {n(lin['ic_inf'], 2)} a {n(lin['ic_sup'], 2)}). "
            f"Ou seja, parte da diferença vinha do veículo, da idade e do horário, mas a maior parte permanece. "
            f"Os outros fatores do modelo também ajudam a calibrar a leitura: dirigir moto ou bicicleta, de madrugada, "
            f"em trecho rural e com 60 anos ou mais pesam muito mais do que o sexo.",
            "Como ler o modelo")
        UI.nota("O modelo usa a base completa, sem filtros, para ter estabilidade. Ele mede associação, não causa: "
                "faltam variáveis como velocidade, uso de cinto/capacete e km rodados.")

    # ---------- Causas ----------
    st.markdown("#### Quais causas aparecem em cada perfil?")
    so_unico = st.toggle("Só acidentes com um único veículo (quando não há dúvida sobre quem dirigia)",
                         value=True, key="c4_unico")
    t, p, teste_c = A.causas_por_sexo(cond, so_unico)
    if len(p) and set(C.SEXOS) <= set(p.columns):
        dif = (p["Masculino"] - p["Feminino"])
        mais_m, mais_f = dif.idxmax(), dif.idxmin()
        titulo = (f"Entre homens pesam mais “{mais_m.lower()}”; entre mulheres, “{mais_f.lower()}”")
        sub = ("% dos condutores de cada sexo por causa principal · " +
               ("acidentes com 1 veículo" if so_unico else "todos os acidentes (a causa é da ocorrência, não do condutor)")
               + (f" · V de Cramér = {n(teste_c['v'], 3)} ({teste_c['efeito']})" if teste_c else ""))
        UI.grafico(G.barras_sexo(p, titulo, sub, "% dos condutores", hover_n=t), t, "c4_causas")
        if not so_unico:
            UI.nota("Num acidente com dois veículos, a mesma causa aparece para os dois motoristas. "
                    "Por isso o recorte de veículo único é o mais confiável para ligar causa a perfil.")

    # ---------- Características ----------
    st.markdown("#### Em que circunstâncias cada um se acidenta?")
    escolha = st.selectbox("Característica da ocorrência", list(CARACTERISTICAS), key="c4_carac")
    col, ordem, top = CARACTERISTICAS[escolha]
    t, p = A.pct_por_sexo(cond, col, top=top, ordem=ordem)
    if len(p) and set(C.SEXOS) <= set(p.columns):
        dif = (p["Masculino"] - p["Feminino"]).abs()
        maior = dif.idxmax()
        tabela = t.copy()
        teste_x = M.qui_quadrado(tabela)
        titulo = (f"A maior diferença está em “{maior}”: {pct(p.loc[maior, 'Feminino'])} das condutoras vs. "
                  f"{pct(p.loc[maior, 'Masculino'])} dos condutores")
        sub = (f"% dos condutores de cada sexo por {escolha.lower()}"
               + (f" · V de Cramér = {n(teste_x['v'], 3)} ({teste_x['efeito']})" if teste_x else ""))
        if ordem:
            p.index = [C.DIA_CURTO.get(i, i) for i in p.index]
            t.index = p.index
        UI.grafico(G.barras_sexo(p, titulo, sub, "% dos condutores", hover_n=t), t, "c4_carac_fig")

    noite = A.pct_por_sexo(cond, "fase_dia", ordem=C.ORDEM_FASE)[1]
    texto_noite = ""
    if "Plena Noite" in noite.index:
        texto_noite = (f" Elas também dirigiam menos à noite ({pct(noite.loc['Plena Noite', 'Feminino'], 0)} contra "
                       f"{pct(noite.loc['Plena Noite', 'Masculino'], 0)}), justamente o período mais letal do KM 2.")
    UI.leitura(
        f"Entre os condutores, a letalidade é de <b>{pct(fem['letalidade'], 2)}</b> para mulheres e "
        f"<b>{pct(mas['letalidade'], 2)}</b> para homens"
        + (f", um risco relativo de {vezes(rr['rr'], 2)}" if rr else "") +
        f". A associação entre sexo e estado físico, porém, tem efeito <b>{teste['efeito'] if teste else '—'}</b> "
        f"(V = {n(teste['v'], 3) if teste else '—'}): o sexo explica pouco da gravidade."
        + texto_noite)
    if not fem["let_ic_sup"] < mas["let_ic_inf"]:
        UI.descoberta(
            "Neste recorte, a letalidade das condutoras <b>não é claramente menor</b> que a dos condutores: os "
            "intervalos de confiança se sobrepõem ou a direção se inverte. Veja o KM 5 para o resultado na base completa.")
        return
    UI.descoberta(
        "Os dados <b>não sustentam</b> a ideia de que acidentes com mulheres ao volante são mais graves: "
        "apontam o contrário. A diferença diminui quando controlamos veículo, idade e horário, mas não "
        "desaparece. Ainda assim, o efeito é pequeno: <b>o tipo de veículo e o horário pesam muito mais "
        "do que o sexo de quem dirige</b>.")
