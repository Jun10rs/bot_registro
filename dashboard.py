from flask import Flask, render_template, request
import json
import os

app = Flask(__name__)

DATA_FILE = "registros.json"

def carregar_registros():
    """Carrega os registros do arquivo JSON."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

@app.route("/")
def index():
    """Exibe a página principal da dashboard."""
    registros = carregar_registros()

    # Filtros opcionais
    nome_filtro = request.args.get("nome", "").strip().lower()
    telefone_filtro = request.args.get("telefone", "").strip()
    data_filtro = request.args.get("data", "").strip()

    if nome_filtro:
        registros = [r for r in registros if nome_filtro in r["nome"].lower()]
    if telefone_filtro:
        registros = [r for r in registros if telefone_filtro in r["telefone"]]
    if data_filtro:
        registros = [r for r in registros if data_filtro in r["data_registro"]]

    return render_template("dashboard.html", registros=registros)

if __name__ == "__main__":
    app.run(debug=True)
