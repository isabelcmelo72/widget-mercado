"""
Vai buscar o Fear and Greed (CNN) e o VIX (Yahoo Finance)
e guarda os valores em data.json.
Só usa bibliotecas que já vêm com o Python.
"""
import json
import sys
import urllib.request
from datetime import datetime, timezone

CABECALHOS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Origin": "https://edition.cnn.com",
    "Referer": "https://edition.cnn.com/",
}

URL_CNN = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
URL_VIX = "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX?interval=5m&range=1d"

CLASSIFICACAO = {
    "extreme fear": "Medo Extremo",
    "fear": "Medo",
    "neutral": "Neutro",
    "greed": "Ganância",
    "extreme greed": "Ganância Extrema",
}


def pedir(url, cabecalhos):
    pedido = urllib.request.Request(url, headers=cabecalhos)
    with urllib.request.urlopen(pedido, timeout=20) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


def buscar_fear_greed():
    dados = pedir(URL_CNN, CABECALHOS)
    fg = dados["fear_and_greed"]
    rating = str(fg["rating"]).lower()
    return {
        "valor": round(float(fg["score"])),
        "classificacao": CLASSIFICACAO.get(rating, rating),
    }


def buscar_vix():
    cab = {"User-Agent": CABECALHOS["User-Agent"], "Accept": "application/json"}
    dados = pedir(URL_VIX, cab)
    meta = dados["chart"]["result"][0]["meta"]
    return {"valor": round(float(meta["regularMarketPrice"]), 2)}


def calcular_cor(fg, vix):
    """Regra da Bússola de Mercado."""
    if fg is None or vix is None:
        return "neutro"
    if fg <= 25 and vix >= 22:
        return "vermelho"
    if fg >= 65 and vix <= 15:
        return "verde"
    return "neutro"


def main():
    resultado = {}
    falhas = []

    for nome, funcao in (("fear_greed", buscar_fear_greed), ("vix", buscar_vix)):
        try:
            resultado[nome] = funcao()
            print(f"OK   {nome}: {resultado[nome]}")
        except Exception as erro:
            resultado[nome] = None
            falhas.append(nome)
            print(f"FALHOU {nome}: {type(erro).__name__}: {erro}")

    fg = resultado["fear_greed"]["valor"] if resultado["fear_greed"] else None
    vix = resultado["vix"]["valor"] if resultado["vix"] else None
    resultado["cor"] = calcular_cor(fg, vix)
    resultado["atualizado_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with open("data.json", "w", encoding="utf-8") as ficheiro:
        json.dump(resultado, ficheiro, ensure_ascii=False, indent=2)

    if falhas:
        print(f"\nRESULTADO: falharam {', '.join(falhas)}")
        sys.exit(1)
    print("\nRESULTADO: os dois valores obtidos com sucesso")


if __name__ == "__main__":
    main()
