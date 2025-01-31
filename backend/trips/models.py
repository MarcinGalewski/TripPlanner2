from django.db import models

class Trip(models.Model):
    id = models.AutoField(primary_key=True)  # ✅ Poprawione ID
    name = models.CharField(max_length=512)
    city = models.CharField(max_length=512)
    start_date = models.DateField()
    end_date = models.DateField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    attractions = models.ManyToManyField('Attraction', related_name='trips')  # ✅ Dodana relacja

class Attraction(models.Model):
    id = models.AutoField(primary_key=True)  # ✅ Poprawione ID
    name = models.CharField(max_length=512)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.CharField(max_length=4096)
