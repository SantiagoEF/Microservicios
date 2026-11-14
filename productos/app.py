from flask import Flask, jsonify, request
app = Flask(__name__)

productos = {
    1: {"id": 1, "nombre": "Laptop", "precio": 12000.0, "stock": 5},
    2: {"id": 2, "nombre": "Mouse", "precio": 250.0, "stock": 20},
    3: {"id": 3, "nombre": "Teclado", "precio": 600.0, "stock": 10},
}

@app.get("/health")
def health():
    return jsonify(servicio="productos", estado="ok")

@app.get("/productos")
def listar():
    return jsonify(list(productos.values()))

@app.get("/productos/<int:pid>")
def obtener(pid):
    if pid not in productos:
        return jsonify(error="Producto no encontrado"), 404
    return jsonify(productos[pid])

@app.post("/productos/<int:pid>/reservar")
def reservar(pid):
    """Descuenta stock. Lo invoca el servicio de pedidos."""
    if pid not in productos:
        return jsonify(error="Producto no encontrado"), 404
    cantidad = (request.get_json(silent=True) or {}).get("cantidad", 1)
    if cantidad <= 0:
        return jsonify(error="Cantidad inválida"), 400
    if productos[pid]["stock"] < cantidad:
        return jsonify(error="Stock insuficiente"), 409
    productos[pid]["stock"] -= cantidad
    return jsonify(productos[pid])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
