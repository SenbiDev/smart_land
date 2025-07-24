from django.db import models

# Create your models here.

class Owner(models.Model):
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

    OWNERSHIP_STATUS_CHOICES=[
        ('full_ownership', 'Full Ownership'),
        ('partial_ownership', 'Partial Ownership'),
        ('investor_owned', 'Investor Owned'),
        ('leashold', 'Leased'),
        ('under_construction', 'Under Construction'),
        ('personal_ownership', 'Personal Ownership'),
    ]

    owner = models.OneToOneField(Owner, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100, choices=ASSET_TYPES)
    location = models.CharField(max_length=100)
    size = models.FloatField()
    value = models.DecimalField(max_digits=20, decimal_places=2)
    acquistion_date = models.DateField()
    ownership_status = models.CharField(max_length=50, choices=OWNERSHIP_STATUS_CHOICES)
    document_url = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

