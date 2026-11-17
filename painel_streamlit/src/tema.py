"""Identidade visual: template Plotly + CSS do Streamlit.

Conceito de UI: "a rodovia da evidência". O painel é uma viagem em 5 quilômetros:
- cabeçalho em asfalto com a faixa amarela tracejada no centro;
- capítulos como marcos quilométricos (KM 1 ... KM 5);
- descobertas em placas (borda amarela) e veredictos de hipótese como sinalização
  (ícone + rótulo, nunca só cor).
Nos gráficos, a interface some: superfície clara, grade em fio, rótulos seletivos.
"""
import plotly.graph_objects as go
import plotly.io as pio

from . import config as C


def registrar_template() -> None:
    t = go.layout.Template()
    t.layout = go.Layout(
        font=dict(family=C.FONTE, size=13, color=C.COR["tinta_2"]),
        title=dict(font=dict(size=16, color=C.COR["tinta"]), x=0, xanchor="left",
                   y=0.98, yanchor="top", pad=dict(b=8)),
        paper_bgcolor=C.COR["superficie"],
        plot_bgcolor=C.COR["superficie"],
        margin=dict(l=8, r=16, t=56, b=8),
        colorway=[C.COR["serie"], C.COR["Feminino"], C.COR["Masculino"]],
        hoverlabel=dict(bgcolor="#ffffff", bordercolor=C.COR["eixo"],
                        font=dict(family=C.FONTE, size=12, color=C.COR["tinta"])),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0,
                    font=dict(size=12, color=C.COR["tinta_2"]), title=dict(text="")),
        xaxis=dict(showgrid=False, linecolor=C.COR["eixo"], linewidth=1, ticks="",
                   tickfont=dict(color=C.COR["tinta_muda"]), zeroline=False,
                   title=dict(font=dict(color=C.COR["tinta_muda"], size=12))),
        yaxis=dict(showgrid=True, gridcolor=C.COR["grade"], gridwidth=1, griddash="solid",
                   linecolor=C.COR["eixo"], showline=False, ticks="", zeroline=False,
                   tickfont=dict(color=C.COR["tinta_muda"]),
                   title=dict(font=dict(color=C.COR["tinta_muda"], size=12))),
        bargap=0.25, bargroupgap=0.08,
        separators=",.",
    )
    pio.templates["prf"] = t
    pio.templates.default = "prf"


CSS = f"""
<style>
:root {{
  --asfalto: {C.COR['asfalto']};
  --asfalto-2: {C.COR['asfalto_2']};
  --faixa: {C.COR['faixa']};
  --placa: {C.COR['placa']};
  --tinta: {C.COR['tinta']};
  --tinta-2: {C.COR['tinta_2']};
  --muda: {C.COR['tinta_muda']};
  --superficie: {C.COR['superficie']};
  --plano: {C.COR['plano']};
  --borda: {C.COR['borda']};
  --fem: {C.COR['Feminino']};
  --mas: {C.COR['Masculino']};
}}
html, body, [class*="css"] {{ font-family: {C.FONTE}; }}
.stApp {{ background: var(--plano); }}
.block-container {{ padding-top: 1.2rem; max-width: 1320px; }}
header[data-testid="stHeader"] {{ background: transparent; }}

/* ---------- Cabeçalho: asfalto + faixa central ---------- */
.hero {{
  background: var(--asfalto); color: #fff; border-radius: 14px;
  padding: 28px 32px 22px; position: relative; overflow: hidden; margin-bottom: 14px;
}}
.hero::after {{
  content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 6px;
  background: repeating-linear-gradient(90deg, var(--faixa) 0 46px, transparent 46px 78px);
  opacity: .95;
}}
.hero .eyebrow {{ color: var(--faixa); font-size: 12px; font-weight: 700;
  letter-spacing: .14em; text-transform: uppercase; }}
.hero h1 {{ color: #fff; font-size: 34px; line-height: 1.15; margin: 6px 0 6px;
  font-weight: 750; padding: 0; }}
.hero p {{ color: #c9cbd0; font-size: 15px; margin: 0; max-width: 820px; }}

/* ---------- Faixa de recorte (filtros ativos) ---------- */
.recorte {{ display: flex; flex-wrap: wrap; gap: 6px; align-items: center;
  font-size: 12.5px; color: var(--tinta-2); margin: 2px 0 10px; }}
.recorte .rot {{ font-weight: 650; color: var(--tinta); margin-right: 2px; }}
.chip {{ background: #fff; border: 1px solid var(--borda); border-radius: 999px;
  padding: 3px 10px; white-space: nowrap; }}
.chip b {{ color: var(--tinta); font-weight: 600; }}

/* ---------- Abertura de capítulo: marco quilométrico ---------- */
.marco {{ display: flex; gap: 18px; align-items: flex-start; margin: 18px 0 8px; }}
.marco .km {{ background: var(--placa); color: #fff; border-radius: 8px; min-width: 74px;
  text-align: center; padding: 8px 6px; font-weight: 800; line-height: 1.05;
  box-shadow: inset 0 0 0 2px rgba(255,255,255,.85); border: 2px solid var(--placa); }}
.marco .km small {{ display: block; font-size: 10px; letter-spacing: .14em; font-weight: 700; opacity: .85; }}
.marco .km span {{ font-size: 24px; }}
.marco h2 {{ font-size: 26px; margin: 0; padding: 0; color: var(--tinta); font-weight: 750; }}
.marco .pergunta {{ font-size: 17px; color: var(--tinta-2); margin-top: 4px; }}

.contexto {{ color: var(--tinta-2); font-size: 15px; line-height: 1.55; max-width: 900px;
  margin: 4px 0 14px; }}

/* ---------- Cards de KPI ---------- */
.kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px;
  margin: 6px 0 14px; }}
.kpi {{ background: var(--superficie); border: 1px solid var(--borda); border-radius: 12px;
  padding: 14px 16px 12px; }}
.kpi .rot {{ font-size: 12.5px; color: var(--tinta-2); font-weight: 600; }}
.kpi .val {{ font-size: 28px; font-weight: 720; color: var(--tinta); margin-top: 2px; }}
.kpi .sub {{ font-size: 12px; color: var(--muda); margin-top: 2px; }}
.kpi .delta {{ font-size: 12px; font-weight: 650; margin-top: 4px; color: var(--tinta-2); }}

/* ---------- Leitura e descoberta ---------- */
.leitura {{ background: var(--superficie); border: 1px solid var(--borda); border-radius: 12px;
  padding: 14px 18px; margin: 8px 0; color: var(--tinta-2); font-size: 14.5px; line-height: 1.55; }}
.leitura h4 {{ margin: 0 0 6px; font-size: 12px; letter-spacing: .12em; text-transform: uppercase;
  color: var(--muda); padding: 0; }}
.leitura b {{ color: var(--tinta); }}
.descoberta {{ background: #fffaf0; border: 1px solid #f3dca6; border-left: 6px solid var(--faixa);
  border-radius: 10px; padding: 14px 18px; margin: 10px 0 18px; font-size: 15px; color: var(--tinta);
  line-height: 1.5; }}
.descoberta .tag {{ font-size: 11px; font-weight: 800; letter-spacing: .14em; color: #8a5d00;
  text-transform: uppercase; display: block; margin-bottom: 4px; }}
.nota {{ font-size: 12px; color: var(--muda); margin: -4px 0 10px; }}

/* ---------- Hipóteses: sinalização ---------- */
.hip {{ background: var(--superficie); border: 1px solid var(--borda); border-radius: 12px;
  padding: 16px 18px; height: 100%; }}
.hip .topo {{ display: flex; justify-content: space-between; align-items: center; gap: 8px; }}
.hip .id {{ font-size: 12px; font-weight: 800; letter-spacing: .12em; color: var(--muda); }}
.selo {{ display: inline-flex; gap: 6px; align-items: center; font-size: 12px; font-weight: 700;
  padding: 3px 10px; border-radius: 999px; border: 1px solid; white-space: nowrap; }}
.selo.confirmada {{ color: #075e07; background: #e9f7e9; border-color: #9fd89f; }}
.selo.nao_confirmada {{ color: #9d2222; background: #fdeceb; border-color: #f0b1ad; }}
.selo.inconclusiva {{ color: #7a5200; background: #fff5dc; border-color: #f3d48a; }}
.hip h3 {{ font-size: 17px; margin: 10px 0 6px; color: var(--tinta); padding: 0; }}
.hip p {{ font-size: 14px; color: var(--tinta-2); margin: 0 0 6px; line-height: 1.5; }}
.hip .ev {{ font-size: 13px; color: var(--tinta); background: var(--plano); border-radius: 8px;
  padding: 8px 10px; margin-top: 8px; }}

/* ---------- Legenda de sexo inline ---------- */
.lg-f {{ color: var(--fem); font-weight: 700; }}
.lg-m {{ color: var(--mas); font-weight: 700; }}
.ponto {{ display: inline-block; width: 10px; height: 10px; border-radius: 3px; margin-right: 4px;
  vertical-align: baseline; }}

/* ---------- Navegação de capítulos ---------- */
div[data-testid="stSegmentedControl"] button, div[data-testid="stButtonGroup"] button {{
  font-weight: 600;
}}
section[data-testid="stSidebar"] {{ background: #fff; border-right: 1px solid var(--borda); }}
section[data-testid="stSidebar"] h2 {{ font-size: 15px; letter-spacing: .02em; }}
div[data-testid="stPlotlyChart"] {{ background: var(--superficie); border: 1px solid var(--borda);
  border-radius: 12px; padding: 6px 8px 2px; }}
.rodape {{ font-size: 12px; color: var(--muda); border-top: 1px solid var(--borda);
  margin-top: 26px; padding-top: 10px; }}
</style>
"""
