"""Formatação de números no padrão brasileiro."""
import math


def n(valor, casas: int = 0) -> str:
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return "—"
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "§").replace(".", ",").replace("§", ".")


def pct(valor, casas: int = 1) -> str:
    return "—" if valor is None or (isinstance(valor, float) and math.isnan(valor)) else n(valor, casas) + "%"


def pp(valor, casas: int = 1) -> str:
    """Diferença em pontos percentuais, com sinal."""
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return "—"
    sinal = "+" if valor > 0 else ("−" if valor < 0 else "±")
    return f"{sinal}{n(abs(valor), casas)} p.p."


def vezes(valor, casas: int = 1) -> str:
    return n(valor, casas) + "×"
