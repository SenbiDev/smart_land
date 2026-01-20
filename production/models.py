from django.db import models
from asset.models import Asset 

class Product(models.Model):
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=50) 
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Production(models.Model):
    STATUS_CHOICES = (
        ('stok', 'Masuk Stok'),
        ('terjual', 'Langsung Terjual'),
    )

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='productions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='production_history')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    
    # [FIX] unit_price kita buat default 0 dan tidak wajib
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True, null=True)
    
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='stok')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.date}"