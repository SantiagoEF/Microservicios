import os
import requests
from flask import Flask, Response, jsonify, request, send_from_directory

app = Flask(__name__)

RUTAS = {
    "usuarios": os.getenv("USUARIOS_URL", "http://localhost:5001"),
    "productos": os.getenv("PRODUCTOS_URL", "http://localhost:5002"),
    "pedidos": os.getenv("PEDIDOS_URL", "http://localhost:5003"),
}

@app.get("/")
def inicio():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "index.html")

@app.get("/health")
def health():
    """Consulta el /health de cada servicio y reporta el estado general."""
    estado = {}
    for nombre, url in RUTAS.items():
        try:
            requests.get(f"{url}/health", timeout=1).raise_for_status()
            estado[nombre] = "ok"
        except requests.RequestException:
            estado[nombre] = "caído"
    return jsonify(estado)

@app.route("/api/<servicio>", defaults={"resto": ""}, methods=["GET", "POST"])
@app.route("/api/<servicio>/<path:resto>", methods=["GET", "POST"])
def proxy(servicio, resto):
    if servicio not in RUTAS:
        return jsonify(error="Ruta desconocida"), 404
    destino = f"{RUTAS[servicio]}/{servicio}" + (f"/{resto}" if resto else "")
    try:
        r = requests.request(
            request.method, destino, json=request.get_json(silent=True), timeout=3
        )
    except requests.RequestException:
        return jsonify(error=f"El servicio '{servicio}' no está disponible"), 503
    return Response(r.content, status=r.status_code, content_type=r.headers["Content-Type"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
