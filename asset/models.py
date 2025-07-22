from django.db import models

# Create your models here.

class KategoriAset(models.Model):
    nama = models.CharField(max_length=50)

    def __str__(self):
        return self.nama
    
class Pemilik(models.Model):
    nama = models.CharField(max_length=100)
    kontak = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.nama
    
class Asset(models.Model):
    ASSET_TYPES = [
        ('lahan', 'Lahan'),
        ('alat', 'Alat'),
        ('bangunan', 'Bangunan'),
        ('ternak', 'Ternak'),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100, choices=ASSET_TYPES)
    locations = models.CharField(max_length=100)
    size = models.FloatField()
    value = models.DecimalField(max_digits=20, decimal_places=2)
    acquistion_date = models.DateField()
    ownership_status = models.CharField(max_length=50)
    document_url = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

