from django.db import models
from django.utils import timezone
from asset.models import Asset

# 1. MASTER PRODUK (Gudang Global)
# Ini yang nanti muncul di Dropdown saat Penjualan
class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nama Produk (Misal: Telur)")
    unit = models.CharField(max_length=20, verbose_name="Satuan (Kg/Liter)")
    
    # Stok Global (Dihitung otomatis saat Produksi/Penjualan)
    current_stock = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Stok Saat Ini")

    def __str__(self):
        return f"{self.name} (Stok: {self.current_stock} {self.unit})"

# 2. RIWAYAT PRODUKSI (Log Panen)
class Production(models.Model):
    QUALITY_CHOICES = [
        ('A', 'Grade A (Sangat Baik)'),
        ('B', 'Grade B (Baik)'),
        ('C', 'Grade C (Cukup)'),
        ('rejected', 'Rejected/Rusak'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, related_name='productions', verbose_name="Asal Aset")
    
    # [UBAH] Link ke Master Product agar nama konsisten
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='production_logs', verbose_name="Pilih Produk")
    
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Jumlah Hasil")
    quality = models.CharField(max_length=20, choices=QUALITY_CHOICES, default='A', verbose_name="Kualitas")
    date = models.DateField(default=timezone.now, verbose_name="Tanggal Panen")

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Saat Panen disimpan -> Tambah Stok Global
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.product.current_stock += self.quantity
            self.product.save()

    def __str__(self):
        return f"Panen {self.product.name} - {self.quantity}"