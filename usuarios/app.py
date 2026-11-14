from flask import Flask, jsonify, request

app = Flask(__name__)

usuarios = {
    1: {"id": 1, "nombre": "Ana Torres", "email": "ana@correo.com"},
    2: {"id": 2, "nombre": "Luis Pérez", "email": "luis@correo.com"},
}
siguiente_id = 3


@app.get("/health")
def health():
    return jsonify(servicio="usuarios", estado="ok")


@app.get("/usuarios")
def listar():
    return jsonify(list(usuarios.values()))


@app.get("/usuarios/<int:uid>")
def obtener(uid):
    if uid not in usuarios:
        return jsonify(error="Usuario no encontrado"), 404
    return jsonify(usuarios[uid])


@app.post("/usuarios")
def crear():
    global siguiente_id
    datos = request.get_json(silent=True) or {}
    if not datos.get("nombre") or not datos.get("email"):
        return jsonify(error="nombre y email son obligatorios"), 400
    nuevo = {"id": siguiente_id, "nombre": datos["nombre"], "email": datos["email"]}
    usuarios[siguiente_id] = nuevo
    siguiente_id += 1
    return jsonify(nuevo), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
