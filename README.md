# CampesinoStock

Sistema de control de inventario para la Agroferretería El Campesino.
Backend en Python (Django), base de datos MySQL/MariaDB (XAMPP), interfaz web con Bootstrap
y un asistente de IA (Gemini) para consultar el inventario en lenguaje natural.

## Requisitos

- Python 3.14
- XAMPP con MySQL/MariaDB encendido
- Una clave de Google AI Studio (solo para el asistente de IA)

## Instalación

1. Crear y activar el entorno virtual, e instalar las dependencias:

   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Crear la base de datos. En phpMyAdmin (`http://localhost/phpmyadmin`), sin entrar a ninguna base,
   ir a **Importar**, elegir `db_campesinostock.sql` y dejar marcada la comprobación de claves foráneas.
   El archivo ya crea la base `db_campesinostock`, sus tablas, las 9 categorías y los 75 productos.

3. Crear el archivo `.env` copiando `.env.example` y pegando la clave de Gemini en `GEMINI_API_KEY`.

4. Confirmar que no falta nada y arrancar:

   ```
   python manage.py migrate
   python manage.py runserver
   ```

   `migrate` no debe aplicar nada nuevo, porque el `.sql` ya incluye las migraciones.

## Primer uso

La base no trae usuarios. Al abrir `http://127.0.0.1:8000/registro/` aparece la **Configuración
inicial**: se crea la cuenta del administrador principal (dueño) y su código secreto. Ese código se
pide después para autorizar nuevas cuentas de administrador. Quien se registra luego queda como
Empleado, y el administrador cambia los roles desde **Empleados**.

## Stock de los productos

Los productos se cargan con stock 0. El stock, el stock mínimo y la ubicación (pasillo y estante)
se editan desde **Productos** con una cuenta de Administrador o Encargado. El asistente de IA siempre
consulta los datos actuales de la base.

## Roles

| | Administrador | Encargado | Empleado |
|---|---|---|---|
| Ver y buscar productos | Sí | Sí | Sí |
| Precio de compra | Sí | Sí | No |
| Crear y editar productos | Sí | Sí | No |
| Eliminar productos | Sí | No | No |
| Proveedores | Todo | Ver, crear y editar | No |
| Empleados y código de autorización | Sí | No | No |
| Asistente de IA | Sí | Sí | Sí |

## Asistente de IA

Menú **Asistente IA**. Ejemplos de preguntas: "¿Qué productos están bajo el mínimo?",
"¿Dónde está el cemento?", "¿Qué debo reabastecer?".

- La IA no accede a la base de datos directamente: solo puede llamar a cuatro funciones del backend
  (buscar productos, productos bajo el mínimo, resumen del inventario y sugerencia de reabastecimiento).
- Los permisos se aplican en el servidor: a un Empleado nunca se le envían precios de compra.
- Si un modelo de Gemini está saturado, se prueba automáticamente el siguiente de la lista.
- Para comprobar la conexión: `python manage.py probar_ia --metodo generate --modelo gemini-3.1-flash-lite`

## Comandos útiles

| Comando | Para qué sirve |
|---|---|
| `python manage.py cargar_productos` | Carga las categorías y los 75 productos |
| `python manage.py probar_ia --listar` | Muestra los modelos de Gemini disponibles |
