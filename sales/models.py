from django.db import models
from django.utils import timezone

class Sale(models.Model):
    # Barang yang dijual
    product_name = models.CharField(max_length=255, verbose_name="Nama Produk Terjual")
    
    # Transaksi
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Jumlah (Qty)")
    unit = models.CharField(max_length=50, verbose_name="Satuan")
    price_per_unit = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Harga Satuan (Rp)")
    
    # Auto-calculated
    total_price = models.DecimalField(max_digits=15, decimal_places=2, editable=False, verbose_name="Total Penjualan")
    
    # Info Pembeli
    buyer_name = models.CharField(max_length=255, null=True, blank=True, default="Umum", verbose_name="Nama Pembeli")
    buyer_contact = models.CharField(max_length=50, null=True, blank=True, verbose_name="Kontak Pembeli")
    
    date = models.DateField(default=timezone.now, verbose_name="Tanggal Transaksi")
    
    # Bukti Pembayaran
    proof_image = models.ImageField(upload_to='sales/', null=True, blank=True, verbose_name="Bukti Pembayaran")
    notes = models.TextField(null=True, blank=True, verbose_name="Catatan")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Penjualan'
        verbose_name_plural = 'Riwayat Penjualan'

    def save(self, *args, **kwargs):
        # Hitung otomatis Total = Qty * Harga
        self.total_price = self.quantity * self.price_per_unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Jual {self.product_name} - Rp {self.total_price:,.0f}"