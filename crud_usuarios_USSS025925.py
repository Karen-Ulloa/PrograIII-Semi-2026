
import hashlib
import base64
import secrets
import hmac
from conexion import conectar



def proteger_clave(clave):
    salt = secrets.token_bytes(8)

    resultado = hashlib.pbkdf2_hmac(
        "sha256",
        clave.encode("utf-8"),
        salt,
        200000,
        dklen=16
    )

    return base64.urlsafe_b64encode(
        salt + resultado
    ).decode("utf-8")



def verificar_clave(clave, guardada):
    try:
        datos = base64.urlsafe_b64decode(guardada.strip())

        salt = datos[:8]
        resultado = datos[8:]

        nueva = hashlib.pbkdf2_hmac(
            "sha256",
            clave.encode("utf-8"),
            salt,
            200000,
            dklen=16
        )

        return hmac.compare_digest(resultado, nueva)

    except Exception:
        return False



def crud_usuarios_USSS025925(accion, datos=None):

    if datos is None:
        datos = {}

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    try:

       
        if accion == "registrar":

            if not datos.get("clave") or len(datos["clave"]) < 6:
                return {
                    "error": "La contraseña debe tener al menos 6 caracteres"
                }

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


        elif accion == "buscar":

            cursor.execute("""
                SELECT idUsuario, usuario, nombre,
                       direccion, telefono
                FROM usuarios_USSS025925
                ORDER BY idUsuario
            """)

            return cursor.fetchall()


        # EDITAR USUARIO
        elif accion == "editar":

            cursor.execute("""
                SELECT idUsuario
                FROM usuarios_USSS025925
                WHERE idUsuario=%s
            """, (datos["idUsuario"],))

            if not cursor.fetchone():
                return {"error": "Usuario no encontrado"}

            nueva_clave = datos.get("clave", "")

            if nueva_clave:
                if len(nueva_clave) < 6:
                    return {
                        "error": "La contraseña debe tener al menos 6 caracteres"
                    }

                sql = """
                    UPDATE usuarios_USSS025925
                    SET usuario=%s,
                        clave=%s,
                        nombre=%s,
                        direccion=%s,
                        telefono=%s
                    WHERE idUsuario=%s
                """

                valores = (
                    datos["usuario"],
                    proteger_clave(nueva_clave),
                    datos["nombre"],
                    datos["direccion"],
                    datos["telefono"],
                    datos["idUsuario"]
                )

            else:
                sql = """
                    UPDATE usuarios_USSS025925
                    SET usuario=%s,
                        nombre=%s,
                        direccion=%s,
                        telefono=%s
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


       
        elif accion == "eliminar":

            cursor.execute("""
                DELETE FROM usuarios_USSS025925
                WHERE idUsuario=%s
            """, (datos["idUsuario"],))

            conexion.commit()

            if cursor.rowcount == 0:
                return {"error": "Usuario no encontrado"}

            return {"mensaje": "Usuario eliminado correctamente"}


       
        elif accion == "login":

            cursor.execute("""
                SELECT idUsuario, usuario, clave
                FROM usuarios_USSS025925
                WHERE usuario=%s
            """, (datos["usuario"],))

            usuario = cursor.fetchone()

            if usuario and verificar_clave(
                datos["clave"],
                usuario["clave"]
            ):
                return {
                    "acceso": True,
                    "idUsuario": usuario["idUsuario"]
                }

            return {"acceso": False}



        elif accion == "cambiar_clave":

            cursor.execute("""
                SELECT clave
                FROM usuarios_USSS025925
                WHERE idUsuario=%s
            """, (datos["idUsuario"],))

            usuario = cursor.fetchone()

            if not usuario:
                return {"error": "Usuario no encontrado"}

            if not verificar_clave(
                datos["clave_actual"],
                usuario["clave"]
            ):
                return {
                    "error": "La contraseña actual es incorrecta"
                }

            nueva_clave = datos["clave_nueva"]

            if not nueva_clave or len(nueva_clave) < 6:
                return {
                    "error": "La nueva contraseña debe tener al menos 6 caracteres"
                }

            cursor.execute("""
                UPDATE usuarios_USSS025925
                SET clave=%s
                WHERE idUsuario=%s
            """, (
                proteger_clave(nueva_clave),
                datos["idUsuario"]
            ))

            conexion.commit()

            return {"mensaje": "Contraseña actualizada correctamente"}


        else:
            return {"error": "Acción no válida"}

    finally:
        cursor.close()
        conexion.close()
