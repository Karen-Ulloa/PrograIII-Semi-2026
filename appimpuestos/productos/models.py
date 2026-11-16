
from django.db import models

class productos(models.Model):
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'productos'
