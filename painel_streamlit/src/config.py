"""Constantes do painel: caminhos, ordens de categorias, paleta e textos fixos.

A paleta foi validada com o validador de daltonismo/contraste (dataviz):
- Sexo: violeta x verde-petróleo, de propósito fora do par rosa/azul,
  que reforçaria o estereótipo que o projeto investiga.
- Gravidade: rampa ordinal de um só matiz (vermelho), do claro (ileso) ao escuro (óbito).
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA_DADOS = RAIZ / "dados"

TABELAS = ["dim_data", "dim_local", "dim_causa", "dim_tipo_acidente",
           "fato_ocorrencia", "fato_envolvido"]

# ---------------- Ordens de categorias ----------------
SEXOS = ["Feminino", "Masculino"]
ORDEM_ESTADO = ["Ileso", "Lesões Leves", "Lesões Graves", "Óbito"]
ORDEM_CLASSIFICACAO = ["Sem Vítimas", "Com Vítimas Feridas", "Com Vítimas Fatais"]
ORDEM_FAIXA = ["0-17", "18-24", "25-34", "35-44", "45-59", "60+"]
ORDEM_DIA = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
             "sexta-feira", "sábado", "domingo"]
DIA_CURTO = {"segunda-feira": "Seg", "terça-feira": "Ter", "quarta-feira": "Qua",
             "quinta-feira": "Qui", "sexta-feira": "Sex", "sábado": "Sáb", "domingo": "Dom"}
ORDEM_FASE = ["Amanhecer", "Pleno dia", "Anoitecer", "Plena Noite"]
MESES_LONGO = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
               "setembro", "outubro", "novembro", "dezembro"]
DIA_FRASE = {"Seg": "às segundas", "Ter": "às terças", "Qua": "às quartas", "Qui": "às quintas",
             "Sex": "às sextas", "Sáb": "aos sábados", "Dom": "aos domingos"}
MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

# Agrupamento de veículos para a análise de confusão (H4)
GRUPO_VEICULO = {
    "Automóvel": "Automóvel",
    "Motocicleta": "Moto", "Motoneta": "Moto", "Ciclomotor": "Moto",
    "Caminhonete": "Caminhonete/utilitário", "Camioneta": "Caminhonete/utilitário",
    "Utilitário": "Caminhonete/utilitário",
    "Caminhão": "Caminhão", "Caminhão-trator": "Caminhão",
    "Ônibus": "Ônibus", "Micro-ônibus": "Ônibus",
    "Bicicleta": "Bicicleta",
}
ORDEM_VEICULO = ["Automóvel", "Moto", "Caminhonete/utilitário", "Caminhão",
                 "Ônibus", "Bicicleta", "Outros"]

# ---------------- Paleta ----------------
COR = {
    # superfícies e tinta
    "superficie": "#fcfcfb",
    "plano": "#f6f5f1",
    "asfalto": "#1f2226",
    "asfalto_2": "#2b2f35",
    "tinta": "#0b0b0b",
    "tinta_2": "#52514e",
    "tinta_muda": "#898781",
    "grade": "#e1e0d9",
    "eixo": "#c3c2b7",
    "borda": "rgba(11,11,11,0.10)",
    # acento de interface (faixa amarela da rodovia) — não é cor de dado
    "faixa": "#eda100",
    "placa": "#0f6b4a",
    # dados
    "serie": "#2a78d6",          # série única
    "serie_apagada": "#c9c8c1",  # ênfase: o que não é foco
    "Feminino": "#6250d6",
    "Masculino": "#0f8a62",
}
COR_ESTADO = dict(zip(ORDEM_ESTADO, ["#e9a197", "#de6b5c", "#b83a32", "#6e1714"]))
COR_CLASSIFICACAO = dict(zip(ORDEM_CLASSIFICACAO, ["#e9a197", "#de6b5c", "#6e1714"]))
RAMPA_SEQUENCIAL = ["#f3f8fe", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5",
                    "#256abf", "#184f95", "#0d366b"]
STATUS = {"confirmada": "#0ca30c", "nao_confirmada": "#d03b3b", "inconclusiva": "#fab219"}

FONTE = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'

# ---------------- Capítulos ----------------
CAPITULOS = [
    ("km1", "KM 1", "O cenário"),
    ("km2", "KM 2", "Onde e quando"),
    ("km3", "KM 3", "Quem se envolve"),
    ("km4", "KM 4", "Investigando as diferenças"),
    ("km5", "KM 5", "Descobertas"),
]

FONTE_DADOS = ("Fonte: PRF — dados abertos de acidentes (datatran, acidentes, todas_causas_tipos), "
               "jan/2024 a ago/2026. Tratamento: notebook Analise_PRF_ETL_SQL.")
