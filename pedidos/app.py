import os
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

USUARIOS_URL = os.getenv("USUARIOS_URL", "http://localhost:5001")
PRODUCTOS_URL = os.getenv("PRODUCTOS_URL", "http://localhost:5002")
TIMEOUT = 2

pedidos = []

@app.get("/health")
def health():
    return jsonify(servicio="pedidos", estado="ok")

@app.get("/pedidos")
def listar():
    return jsonify(pedidos)

@app.post("/pedidos")
def crear():
    datos = request.get_json(silent=True) or {}
    try:
        uid = int(datos["usuario_id"])
        pid = int(datos["producto_id"])
        cantidad = int(datos.get("cantidad", 1))
    except (KeyError, ValueError):
        return jsonify(error="usuario_id, producto_id y cantidad (enteros) requeridos"), 400

    try:
        r_usuario = requests.get(f"{USUARIOS_URL}/usuarios/{uid}", timeout=TIMEOUT)
        if r_usuario.status_code == 404:
            return jsonify(error="El usuario no existe"), 404
        r_usuario.raise_for_status()
        usuario = r_usuario.json()

        r_prod = requests.get(f"{PRODUCTOS_URL}/productos/{pid}", timeout=TIMEOUT)
        if r_prod.status_code == 404:
            return jsonify(error="El producto no existe"), 404
        r_prod.raise_for_status()
        producto = r_prod.json()

        r_res = requests.post(
            f"{PRODUCTOS_URL}/productos/{pid}/reservar",
            json={"cantidad": cantidad},
            timeout=TIMEOUT,
        )
        if r_res.status_code == 409:
            return jsonify(error="Stock insuficiente"), 409
        r_res.raise_for_status()

    except (requests.ConnectionError, requests.Timeout):
        # Tolerancia a fallos: degradamos con un error claro en lugar de colgarnos
        return jsonify(error="Servicio dependiente no disponible, intenta más tarde"), 503

    pedido = {
        "id": len(pedidos) + 1,
        "usuario": usuario["nombre"],
        "producto": producto["nombre"],
        "cantidad": cantidad,
        "total": producto["precio"] * cantidad,
    }
    pedidos.append(pedido)
    return jsonify(pedido), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
