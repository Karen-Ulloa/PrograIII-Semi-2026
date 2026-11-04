import time
from importlib.metadata import PackageNotFoundError, version

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Prueba la conexión con Gemini usando la clave del archivo .env"

    def add_arguments(self, parser):
        parser.add_argument('--timeout', type=int, default=60,
                            help='Segundos máximos de espera (por defecto 60)')
        parser.add_argument('--metodo', choices=['interactions', 'generate'],
                            default='interactions',
                            help='Forma de llamar a la API: interactions (nueva) o generate (clásica)')
        parser.add_argument('--modelo', default='',
                            help='Probar un modelo distinto al del archivo .env')
        parser.add_argument('--listar', action='store_true',
                            help='Mostrar los modelos que tu clave puede usar')

    def handle(self, *args, **options):
        if not settings.GEMINI_API_KEY:
            self.stdout.write(self.style.ERROR(
                "Falta GEMINI_API_KEY. Revisa que tu archivo .env exista junto a manage.py "
                "y que tenga la línea GEMINI_API_KEY=tu_clave"))
            return

        try:
            from google import genai
            from google.genai import errors, types
        except ImportError:
            self.stdout.write(self.style.ERROR(
                "Falta instalar la librería. Ejecuta: pip install -U google-genai"))
            return

        espera = options['timeout']
        metodo = options['metodo']
        modelo = options['modelo'] or settings.GEMINI_MODEL

        try:
            cliente = genai.Client(
                api_key=settings.GEMINI_API_KEY,
                http_options=types.HttpOptions(timeout=espera * 1000),
            )
        except Exception as error:
            self.stdout.write(self.style.ERROR(f"No se pudo crear el cliente: {error}"))
            return

        if options['listar']:
            self.listar_modelos(cliente, errors)
            return

        try:
            self.stdout.write(f"Versión de google-genai: {version('google-genai')}")
        except PackageNotFoundError:
            pass
        self.stdout.write(f"Modelo: {modelo}")
        self.stdout.write(f"Método: {metodo}")
        self.stdout.write(f"Conectando (máximo {espera} segundos)...")

        inicio = time.time()
        try:
            pregunta = "Responde solo con la palabra: listo"
            if metodo == 'interactions' and hasattr(cliente, 'interactions'):
                respuesta = cliente.interactions.create(model=modelo, input=pregunta)
                texto = respuesta.output_text
            else:
                respuesta = cliente.models.generate_content(model=modelo, contents=pregunta)
                texto = respuesta.text
        except errors.APIError as error:
            codigo = getattr(error, 'code', '?')
            mensaje = getattr(error, 'message', str(error))
            self.stdout.write(self.style.ERROR(f"La API respondió con error {codigo}: {mensaje}"))
            return
        except Exception as error:
            segundos = time.time() - inicio
            self.stdout.write(self.style.ERROR(
                f"No se pudo conectar o tardó demasiado ({segundos:.0f} s): {error}"))
            return

        segundos = time.time() - inicio
        self.stdout.write(self.style.SUCCESS(f"Respuesta de Gemini: {texto}"))
        self.stdout.write(f"Tardó {segundos:.1f} segundos.")

    def listar_modelos(self, cliente, errors):
        self.stdout.write("Consultando los modelos disponibles para tu clave...")
        try:
            nombres = []
            for modelo in cliente.models.list():
                nombre = (getattr(modelo, 'name', '') or '').replace('models/', '')
                acciones = getattr(modelo, 'supported_actions', None) or []
                if nombre.startswith('gemini') and (not acciones or 'generateContent' in acciones):
                    nombres.append(nombre)
        except errors.APIError as error:
            self.stdout.write(self.style.ERROR(
                f"Error {getattr(error, 'code', '?')}: {getattr(error, 'message', str(error))}"))
            return
        except Exception as error:
            self.stdout.write(self.style.ERROR(f"No se pudo listar: {error}"))
            return

        if not nombres:
            self.stdout.write("No se encontraron modelos Gemini.")
            return
        for nombre in sorted(set(nombres)):
            self.stdout.write(f"  {nombre}")
        self.stdout.write(self.style.SUCCESS(f"{len(set(nombres))} modelos encontrados."))