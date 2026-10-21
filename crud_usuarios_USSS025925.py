
import hashlib
import base64
import secrets
import hmac
from conexion import conectar


# Proteger la contraseña
def proteger_clave(clave):
    salt = secrets.token_bytes(8)

    resultado = hashlib.pbkdf2_hmac(
        "sha256", clave.encode(), salt, 200000, dklen=16
    )

    return base64.urlsafe_b64encode(
        salt + resultado
    ).decode()


# Verificar la contraseña
def verificar_clave(clave, guardada):
    try:
        datos = base64.urlsafe_b64decode(guardada.strip())
        salt = datos[:8]
        resultado = datos[8:]

        nueva = hashlib.pbkdf2_hmac(
            "sha256", clave.encode(), salt, 200000, dklen=16
        )

        return hmac.compare_digest(resultado, nueva)
    except Exception:
        return False


# CRUD DE USUARIOS
def crud_usuarios_USSS025925(accion, datos=None):

    if datos is None:
        datos = {}

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    try:
        # REGISTRAR
        if accion == "registrar":
            sql = """
                INSERT INTO usuarios_USSS025925
                (usuario, clave, nombre, direccion, telefono)
                VALUES (%s, %s, %s, %s, %s)
            """

            valores = (
                datos["usuario"],
                proteger_clave(datos["clave"]),
                datos["nombre"],
                datos["direccion"],
                datos["telefono"]
            )

            cursor.execute(sql, valores)
            conexion.commit()

            return {"mensaje": "Usuario registrado correctamente"}

        # BUSCAR
        elif accion == "buscar":
            cursor.execute("""
                SELECT idUsuario, usuario, nombre,
                       direccion, telefono
                FROM usuarios_USSS025925
                ORDER BY idUsuario
            """)

            return cursor.fetchall()

        # EDITAR
        elif accion == "editar":
            sql = """
                UPDATE usuarios_USSS025925
                SET usuario=%s, nombre=%s,
                    direccion=%s, telefono=%s
                WHERE idUsuario=%s
            """

            valores = (
                datos["usuario"],
                datos["nombre"],
                datos["direccion"],
                datos["telefono"],
                datos["idUsuario"]
            )

            cursor.execute(sql, valores)
            conexion.commit()

            return {"mensaje": "Usuario actualizado correctamente"}

        # ELIMINAR
        elif accion == "eliminar":
            cursor.execute(
                "DELETE FROM usuarios_USSS025925 WHERE idUsuario=%s",
                (datos["idUsuario"],)
            )

            conexion.commit()

            return {"mensaje": "Usuario eliminado correctamente"}

        # LOGIN
        elif accion == "login":
            cursor.execute("""
                SELECT idUsuario, usuario, clave
                FROM usuarios_USSS025925
                WHERE usuario=%s
            """, (datos["usuario"],))

            usuario = cursor.fetchone()

            if usuario and verificar_clave(
                datos["clave"], usuario["clave"]
            ):
                return {
                    "acceso": True,
                    "idUsuario": usuario["idUsuario"]
                }

            return {"acceso": False}

    finally:
        cursor.close()
        conexion.close()
