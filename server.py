
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from http.cookies import SimpleCookie
from crud_usuarios_USSS025925 import crud_usuarios_USSS025925
import json
import secrets
import time

PORT = 3000

# SESIONES
sesiones = {}


class miServidor(SimpleHTTPRequestHandler):

    def usuario_actual(self):
        cookie = SimpleCookie()

        try:
            cookie.load(self.headers.get("Cookie", ""))
            token = cookie["sesion"].value
        except (KeyError, Exception):
            return None

        datos = sesiones.get(token)

        if not datos:
            return None

        if time.time() > datos["expira"]:
            sesiones.pop(token, None)
            return None

        return datos["usuario"]


    def responder(self, datos, codigo=200, cookie=None):
        respuesta = json.dumps(datos, default=str).encode("utf-8")

        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(respuesta)))
        self.send_header("Cache-Control", "no-store")

        if cookie:
            self.send_header("Set-Cookie", cookie)

        self.end_headers()
        self.wfile.write(respuesta)


    def redirigir(self, ruta, cookie=None):
        self.send_response(302)
        self.send_header("Location", ruta)

        if cookie:
            self.send_header("Set-Cookie", cookie)

        self.end_headers()


    def do_GET(self):
        ruta = urlparse(self.path).path

        if ruta == "/":
            self.path = "/login.html"

        elif ruta == "/registro":
            self.path = "/registro.html"

        elif ruta == "/index.html":
            if not self.usuario_actual():
                self.redirigir("/")
                return

        elif ruta == "/buscar":
            if not self.usuario_actual():
                self.responder({"error": "Acceso denegado"}, 401)
                return

            try:
                datos = crud_usuarios_USSS025925("buscar")
                self.responder(datos)
            except Exception:
                self.responder({"error": "Error al consultar usuarios"}, 500)
            return

        elif ruta == "/salir":
            cookie = SimpleCookie()
            cookie.load(self.headers.get("Cookie", ""))

            if "sesion" in cookie:
                sesiones.pop(cookie["sesion"].value, None)

            self.redirigir(
                "/",
                "sesion=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0"
            )
            return

        return super().do_GET()


    def do_POST(self):
        ruta = urlparse(self.path).path

        rutas = [
            "/registrar",
            "/login",
            "/editar",
            "/eliminar",
            "/cambiar_clave"
        ]

        if ruta not in rutas:
            self.responder({"error": "Ruta no encontrada"}, 404)
            return

        if ruta in ["/editar", "/eliminar", "/cambiar_clave"]:
            if not self.usuario_actual():
                self.responder({"error": "Acceso denegado"}, 401)
                return

        try:
            longitud = int(self.headers.get("Content-Length", 0))

            if longitud <= 0 or longitud > 10000:
                self.responder({"error": "Datos no válidos"}, 400)
                return

            datos = json.loads(
                self.rfile.read(longitud).decode("utf-8")
            )

            if not isinstance(datos, dict):
                self.responder({"error": "Datos no válidos"}, 400)
                return

            if ruta == "/registrar":
                resultado = crud_usuarios_USSS025925(
                    "registrar", datos
                )

            elif ruta == "/login":
                resultado = crud_usuarios_USSS025925(
                    "login", datos
                )

                if resultado["acceso"]:
                    token = secrets.token_urlsafe(32)

                    sesiones[token] = {
                        "usuario": resultado["idUsuario"],
                        "expira": time.time() + 3600
                    }

                    self.responder(
                        resultado,
                        cookie=f"sesion={token}; HttpOnly; SameSite=Lax; Path=/"
                    )
                    return

            elif ruta == "/editar":
                resultado = crud_usuarios_USSS025925(
                    "editar", datos
                )

            elif ruta == "/eliminar":
                resultado = crud_usuarios_USSS025925(
                    "eliminar", datos
                )

            elif ruta == "/cambiar_clave":
                resultado = crud_usuarios_USSS025925(
                    "cambiar_clave", datos
                )

            if "error" in resultado:
                self.responder(resultado, 400)
            else:
                self.responder(resultado)

        except (ValueError, KeyError, TypeError):
            self.responder(
                {"error": "Datos incompletos o incorrectos"}, 400
            )

        except Exception as e:
            print("Error:", e)
            self.responder(
                {"error": "Error al procesar la solicitud"}, 500
            )


print(f"Servidor ejecutándose en http://localhost:{PORT}")

HTTPServer(("localhost", PORT), miServidor).serve_forever()
