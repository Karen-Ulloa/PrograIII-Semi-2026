from django.contrib import admin
from .models import *

# Esto registra todos tus modelos automáticamente
from django.apps import apps
models = apps.get_app_config('inventario').get_models()
for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass