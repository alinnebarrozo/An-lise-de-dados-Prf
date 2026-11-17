# “Mulher no volante, perigo constante?”
### Painel interativo de data storytelling com os dados de acidentes da PRF (jan/2024 – ago/2026)

O painel conduz o público por uma **viagem de cinco quilômetros**, da pergunta à descoberta. Cada capítulo tem pergunta central, contexto, evidência, interpretação e descoberta.

| Capítulo | Pergunta | Evidência principal |
|---|---|---|
| **KM 1 · O cenário** | Qual é o tamanho do problema? | KPIs, evolução mensal, gravidade por ano, comparação de períodos na mesma janela |
| **KM 2 · Onde e quando** | Há concentração no espaço e no tempo? | Mapa, rankings de UF/BR/município (volume ou letalidade), calendário dia × hora, fase do dia, sazonalidade |
| **KM 3 · Quem se envolve** | Qual é o perfil das pessoas? | Sexo por papel na ocorrência, idade, veículo, gravidade por papel |
| **KM 4 · Investigando as diferenças** | A diferença de gênero se sustenta? | Taxas com IC 95%, χ² e V de Cramér, estratificação, regressão logística, causas, circunstâncias |
| **KM 5 · Descobertas** | O ditado se sustenta? | Veredictos das hipóteses H1–H4 por regra, limitações, qualidade dos dados |

## Principais resultados (base completa)

- Mulheres são **11,9%** dos condutores envolvidos e **56,8%** dos passageiros.
- Letalidade entre condutores: **1,73%** para mulheres (IC 95%: 1,60–1,86) e **3,58%** para homens (IC 95%: 3,51–3,65).
- A associação entre sexo e estado físico é **muito pequena** (V de Cramér = 0,070).
- Com ajuste por veículo, idade, fase do dia, trecho e dia da semana, a razão de chances de óbito (homem ÷ mulher) cai de **2,09** para **1,76** (IC 95%: 1,62–1,91). A diferença diminui, mas persiste.
- Veículo (moto, bicicleta), madrugada, trecho rural e idade 60+ pesam mais na gravidade do que o sexo.

**Limitação central:** a base não tem dado de exposição (km rodados, condutores por sexo). Nenhum indicador é risco por motorista, e os resultados mostram associação, não causa.

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```

O painel abre em `http://localhost:8501`.

**Publicar (gratuito):** suba a pasta para um repositório no GitHub, incluindo `dados/*.parquet` (cerca de 12 MB), e crie o app em [share.streamlit.io](https://share.streamlit.io) apontando para `app.py`.

## Atualizar os dados

1. Rode o notebook de ETL (`Analise_PRF_ETL_SQL`) com os novos arquivos da PRF.
2. Copie os parquets de `saida/modelo_estrela/`, junto com `registro_qualidade.csv` e `dicionario_kpis.csv`, para `dados/`.
3. Reabra o painel. O cache é invalidado quando os arquivos mudam, e títulos, textos e veredictos são recalculados.

## Arquitetura

```
app.py                      # página, filtros, navegação entre capítulos
src/
  config.py                 # caminhos, ordens de categorias, paleta validada
  dados.py                  # carga do modelo estrela e junção fato + dimensões
  filtros.py                # lógica de filtros (respeita o grão de cada tabela)
  metricas.py               # KPIs, IC de Wilson, χ², V de Cramér, risco relativo, regressão logística (IRLS)
  analises.py               # agregações de cada capítulo
  graficos.py               # figuras Plotly
  tema.py                   # template Plotly + CSS (identidade visual)
  componentes.py            # blocos de interface (KPIs, leitura, descoberta, hipóteses)
  capitulos/cap1 … cap5     # narrativa de cada capítulo
testes/test_reconciliacao.py  # confere o painel contra os números do notebook
```

### Decisões de método

- **Grão:** ocorrências e pessoas nunca são misturadas. Filtros de pessoa (sexo, faixa etária, tipo de envolvido) fazem os KPIs de ocorrência contarem "acidentes com ao menos um envolvido no recorte".
- **Denominadores:** letalidade e gravidade usam envolvidos com estado físico informado, como no dicionário de KPIs. Comparações por sexo usam os condutores de cada sexo.
- **Significância vs. efeito:** com 300 mil registros, quase tudo dá p < 0,05. Por isso toda diferença vem com IC 95% e com V de Cramér ou razão de chances.
- **Causa da ocorrência:** a causa é registrada por acidente, não por condutor. A análise de causas prioriza acidentes com um único veículo.
- **Achado de qualidade (novo no painel):** cerca de 27 mil condutores tinham idade 0, um valor padrão de preenchimento. Nas análises de idade, essa idade é tratada como não informada.
- **2026 parcial:** a comparação entre anos usa a mesma janela de meses. A sazonalidade usa só anos completos.

### Design (UI/UX)

- **Metáfora da rodovia:** cabeçalho em asfalto com faixa amarela tracejada; capítulos como marcos quilométricos verdes, no padrão das placas brasileiras; descobertas em "placas" com borda amarela.
- **Títulos que afirmam:** cada gráfico tem um título-mensagem calculado a partir dos dados (por exemplo, "Mulheres são 12% de quem dirigia, mas 57% de quem estava de carona"), que se atualiza com os filtros.
- **Cores com função:** Feminino em violeta e Masculino em verde-petróleo, fora do par rosa/azul que reforçaria o estereótipo investigado. A gravidade usa uma rampa ordinal de um só matiz (vermelho), validada para daltonismo e contraste.
- **Acessibilidade:** veredictos com ícone e rótulo, não só cor; cada gráfico tem "Ver os números deste gráfico"; um eixo por gráfico; rótulos diretos seletivos.

## Ferramentas

Python · pandas · NumPy · SciPy · Plotly · Streamlit. Os dados vêm do ETL em pandas e SQL (DuckDB), com modelo estrela em parquet.
