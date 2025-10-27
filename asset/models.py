from django.db import models

# Pemilik Lahan/Aset Fisik
class Owner(models.Model):
    nama = models.CharField(max_length=100)
    kontak = models.CharField(max_length=100, null=True, blank=True)
    alamat = models.TextField(null=True, blank=True)
    
    # Info rekening untuk transfer bagi hasil
    nomor_rekening = models.CharField(max_length=50, null=True, blank=True)
    bank = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.nama

class Asset(models.Model):
    ASSET_TYPES = [
        ('lahan', 'Lahan'),
        ('alat', 'Alat'),
        ('bangunan', 'Bangunan'),
        ('ternak', 'Ternak'),
    ]

    OWNERSHIP_STATUS_CHOICES = [
        ('full_ownership', 'Full Ownership'),
        ('partial_ownership', 'Partial Ownership'),
        ('investor_owned', 'Investor Owned'),
        ('leashold', 'Leased'),
        ('under_construction', 'Under Construction'),
        ('personal_ownership', 'Personal Ownership'),
    ]

    # ✅ ForeignKey - 1 Owner bisa punya banyak Asset
    landowner = models.ForeignKey(
        Owner, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='assets',
        verbose_name='Pemilik Lahan'
    )
    
    name = models.CharField(max_length=100, verbose_name='Nama Aset')
    type = models.CharField(max_length=100, choices=ASSET_TYPES, verbose_name='Tipe Aset')
    location = models.CharField(max_length=100, verbose_name='Lokasi')
    size = models.FloatField(verbose_name='Ukuran (m²)')
    value = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='Nilai Aset')
    acquisition_date = models.DateField(verbose_name='Tanggal Akuisisi')
    ownership_status = models.CharField(
        max_length=50, 
        choices=OWNERSHIP_STATUS_CHOICES,
        verbose_name='Status Kepemilikan'
    )
    document_url = models.TextField(null=True, blank=True, verbose_name='Dokumen')
    created_at = models.DateTimeField(auto_now_add=True)

    # Persentase bagi hasil untuk pemilik lahan (default 10%)
    landowner_share_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=10.00,
        verbose_name='% Bagi Hasil Pemilik'
    )

    def __str__(self):
        return self.name

    @property
    def investors(self):
        """Daftar investor yang berinvestasi di aset ini"""
        return [o.investor for o in self.ownerships.all()]
    
    @property
    def total_investment(self):
        """Total investasi yang masuk ke aset ini"""
        from django.db.models import Sum
        total = self.ownerships.aggregate(
            total=Sum('funding__amount')
        )['total']
        return total or 0

    class Meta:
        verbose_name = 'Aset'
        verbose_name_plural = 'Aset'