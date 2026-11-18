# 🚗 Análise Exploratória de Dados (EDA) — Acidentes nas Rodovias Federais | PRF

## 🛣️ Painel interativo: “Mulher no volante, perigo constante?”

**Acesse o painel:** https://alinnebarrozo.github.io/Analise_dados_Prf/

Painel de *data storytelling* em 5 capítulos (KM 1 a KM 5), construído sobre o modelo estrela gerado pelo ETL deste repositório:

| Capítulo | Pergunta |
|---|---|
| KM 1 · O cenário | Qual é o tamanho do problema? |
| KM 2 · Onde e quando | Os acidentes se concentram em lugares e horários específicos? |
| KM 3 · Quem se envolve | Qual é o perfil das pessoas envolvidas? |
| KM 4 · Investigando as diferenças | A diferença entre condutoras e condutores se sustenta? |
| KM 5 · Descobertas | O ditado se sustenta? |

**Principais resultados:**
- Mulheres são 11,9% dos condutores envolvidos e 56,8% dos passageiros.
- Letalidade entre condutores: 1,73% para mulheres e 3,58% para homens.
- A associação entre sexo e gravidade é muito pequena (V de Cramér = 0,070).
- Com ajuste por veículo, idade, fase do dia, trecho e dia da semana, a razão de chances de óbito (homem ÷ mulher) cai de 2,09 para 1,76. A diferença diminui, mas persiste.
- A base não tem dado de exposição (km rodados, condutores por sexo), e os resultados indicam associação, não causa.

**Onde está cada parte:**
- `docs/`: versão web do painel (HTML + JavaScript + Plotly), publicada no GitHub Pages.
- `painel_streamlit/`: versão em Python (Streamlit + Plotly), com testes que conferem o painel contra os números do notebook. Veja o `README` da pasta para rodar.
- `Analise_PRF_ETL_SQL_Modelo.ipynb`: ETL, integração em SQL (DuckDB) e modelo estrela.

---

## 1. Sobre o projeto

Este projeto tem como objetivo realizar uma Análise Exploratória de Dados (EDA) a partir de dados públicos disponibilizados pela **Polícia Rodoviária Federal (PRF)**, relacionados aos acidentes registrados nas rodovias federais brasileiras.

A análise busca compreender a estrutura e as características dos dados, identificar padrões, explorar distribuições e investigar possíveis relações entre as variáveis presentes nas bases.

Um dos direcionamentos da investigação é explorar a participação de homens e mulheres nas ocorrências, buscando identificar possíveis diferenças nos perfis das pessoas envolvidas e nas características dos acidentes.

## 2. Fonte de dados

Os dados utilizados são provenientes dos registros públicos de acidentes disponibilizados pela Polícia Rodoviária Federal.

Foram consideradas bases com diferentes perspectivas sobre os registros:

- **Acidentes:** informações relacionadas às ocorrências registradas.
- **Pessoas:** informações sobre as pessoas envolvidas nos acidentes.
- **Pessoas — causas e tipos:** informações complementares relacionadas às pessoas, causas e classificações dos acidentes.

A utilização dessas bases permite explorar diferentes dimensões dos registros, respeitando as particularidades e os níveis de granularidade de cada conjunto de dados.

## 3. Objetivos da análise exploratória

A EDA foi conduzida com os seguintes objetivos:

- Compreender a estrutura e a qualidade dos conjuntos de dados.
- Identificar tipos de variáveis e características dos registros.
- Investigar valores ausentes e possíveis inconsistências.
- Explorar a distribuição das ocorrências e das pessoas envolvidas.
- Identificar padrões temporais e características dos acidentes.
- Explorar a distribuição por gênero e outras características demográficas disponíveis.
- Investigar possíveis associações entre gênero, tipo de acidente e gravidade das ocorrências.
- Identificar oportunidades para aprofundamento das análises.

## 4. Metodologia

A análise foi desenvolvida utilizando Python em ambiente Google Colab, seguindo etapas de exploração e preparação dos dados.

### Etapas desenvolvidas

**1. Carregamento dos dados**
- Importação das bases disponibilizadas pela PRF.
- Leitura dos arquivos CSV.
- Configuração dos parâmetros de leitura, considerando separador e codificação dos arquivos.

**2. Conhecimento e exploração das bases**
- Verificação das dimensões dos DataFrames.
- Identificação das colunas e tipos de dados.
- Análise das primeiras observações.
- Verificação da estrutura e granularidade dos registros.

**3. Qualidade e preparação dos dados**
- Investigação de valores ausentes.
- Verificação de possíveis duplicidades.
- Avaliação da consistência das informações.
- Identificação de variáveis relevantes para as análises.

**4. Análise exploratória univariada e bivariada**
- Exploração da distribuição das variáveis.
- Análise de frequências e proporções.
- Comparação entre categorias.
- Investigação de possíveis relações entre características dos acidentes e das pessoas envolvidas.

**5. Investigação das diferenças por gênero**

Uma das frentes da análise consiste em explorar a participação de homens e mulheres nos registros, considerando as variáveis disponíveis nas bases.

O objetivo é investigar possíveis diferenças nos padrões observados, sem estabelecer previamente conclusões ou relações de causalidade.

## 5. Tecnologias e ferramentas

- **Python:** linguagem utilizada no desenvolvimento da análise.
- **Google Colab:** ambiente de desenvolvimento.
- **Pandas:** manipulação e exploração dos dados.
- **NumPy:** operações e processamento numérico.
- **Matplotlib / Seaborn:** visualização e exploração gráfica, quando aplicável.

## 6. Abordagem analítica

A análise utiliza uma abordagem exploratória orientada por perguntas, buscando transformar os registros disponíveis em informações relevantes.

A investigação considera a importância de distinguir:
- Quantidade absoluta de ocorrências.
- Frequência relativa e proporções.
- Distribuição das pessoas envolvidas.
- Características das ocorrências.
- Diferenças entre grupos.

Também são considerados os diferentes níveis de granularidade das bases, evitando comparações inadequadas entre registros de acidentes e registros de pessoas.

## 7. Considerações e limitações

Os dados representam ocorrências registradas pela Polícia Rodoviária Federal e, portanto, suas características e limitações devem ser consideradas na interpretação dos resultados.

A análise exploratória não permite, isoladamente, estabelecer relações de causalidade.

Além disso, comparações entre gêneros devem considerar a unidade de análise, os denominadores e a composição dos grupos observados.

## 8. Objetivo desta etapa

A EDA constitui a etapa inicial de investigação do projeto, permitindo conhecer os dados, avaliar sua qualidade, identificar padrões e formular perguntas analíticas mais aprofundadas.

O foco desta etapa é construir uma base consistente para interpretar os dados e fundamentar as próximas etapas de desenvolvimento analítico.

---

**Projeto desenvolvido para fins de estudo e portfólio em Ciência de Dados, utilizando dados públicos da Polícia Rodoviária Federal.**
