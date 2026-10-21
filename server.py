
from flask import Flask, request, jsonify, send_from_directory, session, redirect
from crud_usuarios_USSS025925 import crud_usuarios_USSS025925
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

@app.route("/")
def inicio():
    return send_from_directory(".", "login.html")

@app.route("/registro")
def pagina_registro():
    return send_from_directory(".", "registro.html")

@app.route("/index.html")
def pagina_usuarios():
    if "usuario" not in session:
        return redirect("/")
    return send_from_directory(".", "index.html")

@app.route("/app.js")
def javascript():
    return send_from_directory(".", "app.js")

@app.route("/registrar", methods=["POST"])
def registrar():
    datos = request.get_json()
    resultado = crud_usuarios_USSS025925("registrar", datos)
    return jsonify(resultado)

@app.route("/login", methods=["POST"])
def login():
    datos = request.get_json()
    resultado = crud_usuarios_USSS025925("login", datos)

    if resultado["acceso"]:
        session["usuario"] = resultado["idUsuario"]

    return jsonify(resultado)

@app.route("/buscar")
def buscar():
    if "usuario" not in session:
        return jsonify({"error": "Acceso denegado"}), 401

    resultado = crud_usuarios_USSS025925("buscar")
    return jsonify(resultado)

@app.route("/editar", methods=["POST"])
def editar():
    if "usuario" not in session:
        return jsonify({"error": "Acceso denegado"}), 401

    datos = request.get_json()
    resultado = crud_usuarios_USSS025925("editar", datos)
    return jsonify(resultado)

@app.route("/eliminar", methods=["POST"])
def eliminar():
    if "usuario" not in session:
        return jsonify({"error": "Acceso denegado"}), 401

    datos = request.get_json()
    resultado = crud_usuarios_USSS025925("eliminar", datos)
    return jsonify(resultado)

@app.route("/salir")
def salir():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, port=3000)
