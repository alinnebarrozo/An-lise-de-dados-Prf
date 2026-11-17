"""Confere se o painel reproduz os números do notebook de EDA/ETL.

Rodar:  python -m pytest testes -q
Valores de referência: saídas impressas no notebook Analise_PRF_ETL_SQL (seções 5, 9 e 10).
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src import analises as A  # noqa: E402
from src import metricas as M  # noqa: E402
from src.dados import carregar_base  # noqa: E402
from src.filtros import Filtros, aplicar  # noqa: E402


@pytest.fixture(scope="module")
def base():
    return carregar_base()


def test_contagens_do_etl(base):
    assert len(base.ocorrencias) == 194_443
    assert len(base.envolvidos) == 477_650


def test_obitos_conferem_entre_bases(base):
    assert base.envolvidos["obito"].sum() == base.ocorrencias["mortos"].sum() == 16_327


def test_kpis_por_ano(base):
    k = A.kpis_por_ano(base.ocorrencias, base.envolvidos).set_index("ano")
    esperado = {2024: (73_202, 7.14, 3.68, 15.85), 2025: (72_529, 7.18, 3.64, 15.70),
                2026: (48_712, 7.17, 3.64, 15.49)}
    for ano, (oc, fatais, let, grav) in esperado.items():
        assert k.loc[ano, "ocorrencias"] == oc
        assert round(k.loc[ano, "pct_ocorrencias_fatais"], 2) == pytest.approx(fatais, abs=0.01)
        assert round(k.loc[ano, "letalidade"], 2) == pytest.approx(let, abs=0.01)
        assert round(k.loc[ano, "gravidade"], 2) == pytest.approx(grav, abs=0.01)


def test_tabela_sexo_estado_e_cramer(base):
    cond = M.condutores_com_sexo(base.envolvidos)
    tab, teste = A.teste_sexo_estado(cond)
    assert tab.loc["Feminino"].tolist() == [15_913, 15_981, 3_756, 626]
    assert tab.loc["Masculino"].tolist() == [134_742, 92_417, 32_116, 9_614]
    assert teste["v"] == pytest.approx(0.070, abs=0.0005)


def test_causas_veiculo_unico(base):
    cond = M.condutores_com_sexo(base.envolvidos)
    _, p, _ = A.causas_por_sexo(cond, veiculo_unico=True)
    assert p.loc["Ingestão de álcool pelo condutor", "Masculino"] == pytest.approx(7.28, abs=0.01)
    assert p.loc["Ausência de reação do condutor", "Feminino"] == pytest.approx(22.51, abs=0.01)


def test_filtro_de_pessoa_nao_duplica_ocorrencias(base):
    oc, ev = aplicar(base.ocorrencias, base.envolvidos, Filtros(sexos=("Feminino",)))
    assert oc["id"].is_unique
    assert set(oc["id"]) == set(ev["id"])


def test_regressao_converge(base):
    reg = M.modelo_ajustado(base.envolvidos)
    linha = reg[reg["termo"] == "sexo=Masculino"].iloc[0]
    assert linha["ic_inf"] > 1  # a diferença persiste com ajuste
    assert pd.notna(reg["ep"]).all()
