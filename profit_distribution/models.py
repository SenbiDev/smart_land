from django.db import models
from django.utils import timezone
from django.db.models import Sum

# Import model lain untuk perhitungan
# Kita gunakan string reference atau import di dalam method untuk hindari circular import jika perlu
from asset.models import Asset
from funding.models import Funding

class ProfitDistribution(models.Model):
    # Field Input Admin
    date = models.DateField(default=timezone.now, verbose_name="Tanggal Pembagian")
    total_distributed = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Total Dana Dibagikan (Rp)")
    
    # Field Hasil Hitungan (Read Only secara konsep)
    landowner_total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, editable=False, verbose_name="Total Jatah Landowner")
    investor_total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, editable=False, verbose_name="Total Jatah Investor")
    
    retained_earnings = models.DecimalField(max_digits=15, decimal_places=2, default=0, editable=False, verbose_name="Sisa Dana (Retained)")
    dividend_per_share = models.DecimalField(max_digits=15, decimal_places=2, default=0, editable=False, verbose_name="Dividen Per Lembar")

    # Menyimpan rincian teks panjang agar admin bisa baca history siapa dapet berapa
    distribution_details = models.TextField(blank=True, verbose_name="Rincian Hasil (Otomatis)")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Bagi Hasil'
        verbose_name_plural = 'Riwayat Bagi Hasil'

    def __str__(self):
        return f"Distribusi {self.date} - Rp {self.total_distributed:,.0f}"

    def save(self, *args, **kwargs):
        # --- LOGIKA OTOMATIS (CORE LOGIC) ---
        
        # 1. Hitung Jatah Landowner
        # (Sesuai request: Dipotong langsung persenan dari Total Dana)
        active_assets = Asset.objects.all() # Nanti bisa filter(status='active')
        total_landowner_cut = 0
        details_text = "=== RINCIAN LANDOWNER ===\n"

        for asset in active_assets:
            # Rumus: (Total Dana * Persen Aset) / 100
            if asset.landowner_share_percentage > 0:
                cut = (self.total_distributed * asset.landowner_share_percentage) / 100
                total_landowner_cut += cut
                details_text += f"- {asset.name} ({asset.landowner_share_percentage}%): Rp {cut:,.0f}\n"

        self.landowner_total_amount = total_landowner_cut

        # 2. Sisa untuk Investor
        net_for_investors = self.total_distributed - self.landowner_total_amount
        
        # 3. Hitung Dividen Per Lembar
        # Coba ambil Total Saham Sistem dari Config, kalau error pakai default 15.000
        try:
            from dashboard.models import SystemConfig
            config = SystemConfig.objects.first()
            TOTAL_SYSTEM_SHARES = config.total_system_shares if config else 15000
        except:
            TOTAL_SYSTEM_SHARES = 15000 
        
        if net_for_investors > 0:
            self.dividend_per_share = net_for_investors / TOTAL_SYSTEM_SHARES
        else:
            self.dividend_per_share = 0

        # 4. Hitung Realisasi Payout (Hanya ke saham yg laku)
        sold_shares = Funding.objects.filter(source_type='investor').aggregate(Sum('shares'))['shares__sum'] or 0
        
        real_investor_payout = sold_shares * self.dividend_per_share
        self.investor_total_amount = real_investor_payout

        # 5. Hitung Retained Earnings (Uang balik ke kas dari saham kosong)
        self.retained_earnings = net_for_investors - real_investor_payout

        # 6. Update Text Laporan Lengkap
        details_text += f"\n=== RINCIAN INVESTOR ===\n"
        details_text += f"Dana Net Saham: Rp {net_for_investors:,.0f}\n"
        details_text += f"Total Saham Sistem: {TOTAL_SYSTEM_SHARES} lbr\n"
        details_text += f"Dividen/Lembar: Rp {self.dividend_per_share:,.2f}\n"
        details_text += f"Saham Terjual: {sold_shares} lbr -> Total Bayar: Rp {real_investor_payout:,.0f}\n"
        details_text += f"Kembali ke Kas (Retained): Rp {self.retained_earnings:,.0f}"
        
        self.distribution_details = details_text

        super().save(*args, **kwargs)