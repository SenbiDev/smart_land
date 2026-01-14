from django.db import models
from django.utils import timezone
from asset.models import Asset

class Production(models.Model):
    QUALITY_CHOICES = [
        ('A', 'Grade A (Sangat Baik)'),
        ('B', 'Grade B (Baik)'),
        ('C', 'Grade C (Cukup)'),
        ('rejected', 'Rejected/Rusak'),
    ]

    # Sumber Hasil (Dari Aset mana?)
    # on_delete=models.SET_NULL: Jika aset dihapus, riwayat panen TETAP ADA (penting untuk laporan)
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, related_name='productions', verbose_name="Asal Aset")
    
    # Detail Produk
    product_name = models.CharField(max_length=255, verbose_name="Nama Produk")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Jumlah")
    unit = models.CharField(max_length=50, verbose_name="Satuan", help_text="Contoh: Kg, Liter, Ikat")
    quality = models.CharField(max_length=20, choices=QUALITY_CHOICES, default='A', verbose_name="Kualitas/Grade")
    
    date = models.DateField(default=timezone.now, verbose_name="Tanggal Panen")
    notes = models.TextField(null=True, blank=True, verbose_name="Catatan")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Stok Masuk (Produksi)'
        verbose_name_plural = 'Riwayat Produksi'

    def __str__(self):
        return f"{self.product_name} - {self.quantity} {self.unit}"