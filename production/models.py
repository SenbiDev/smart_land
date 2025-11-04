from django.db import models
from asset.models import Asset  

# Create your models here.
class Production(models.Model):
    
    # --- TAMBAHAN BARU ---
    STATUS_CHOICES = [
        ('stok', 'Stok'),
        ('terjual', 'Terjual'),
    ]
    # ---------------------

    name = models.CharField(max_length=255)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='productions')
    date = models.DateField()
    quantity = models.FloatField()
    unit = models.CharField(max_length=50)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # --- FIELD BARU ---
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='stok', # <-- PENTING: default untuk data lama
        db_index=True 
    )
    # ------------------
    
    def __str__(self):
        return f"Production of {self.asset.name} on {self.date}"