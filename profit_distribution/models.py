from django.db import models
from django.utils import timezone

class ProfitDistribution(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft (Konsep)'),
        ('distributed', 'Distributed (Sudah Dibagikan)'),
    ]

    period = models.CharField(max_length=100, verbose_name="Periode", help_text="Contoh: Januari 2026")
    date = models.DateField(default=timezone.now, verbose_name="Tanggal Pembagian")
    
    # Keuangan
    total_distributed = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Total Dana Dibagikan")
    landowner_share = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Total Jatah Pemilik Lahan")
    investor_share = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Total Jatah Investor")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Status")
    notes = models.TextField(null=True, blank=True, verbose_name="Catatan")
    
    # [FLEXIBLE] Menyimpan detail per orang dalam JSON
    # Format data nanti: [{"nama": "Budi", "tipe": "Investor", "jumlah": 500000}, ...]
    details = models.JSONField(default=dict, verbose_name="Detail Pembagian") 

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Bagi Hasil'
        verbose_name_plural = 'Riwayat Bagi Hasil'

    def __str__(self):
        return f"Bagi Hasil {self.period} - Rp {self.total_distributed:,.0f}"