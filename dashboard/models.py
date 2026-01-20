from django.db import models
from django.db.models import Sum

class SystemConfig(models.Model):
    # Konfigurasi Saham
    total_system_shares = models.PositiveIntegerField(default=15000, verbose_name="Total Lembar Saham Disediakan")
    share_price = models.DecimalField(max_digits=15, decimal_places=2, default=100000, verbose_name="Harga Per Lembar")

    class Meta:
        verbose_name = "Dashboard & Konfigurasi"
        verbose_name_plural = "Dashboard & Konfigurasi"

    def __str__(self):
        return "Pengaturan Sistem & Laporan Global"

    # --- FUNGSI HITUNG DATA (LENGKAP) ---

    def total_assets(self):
        """Jumlah unit aset (Count)"""
        from asset.models import Asset
        return Asset.objects.count()

    def total_asset_value(self):
        """Total nilai uang aset (Sum Value)"""
        from asset.models import Asset
        return Asset.objects.aggregate(Sum('value'))['value__sum'] or 0

    def total_funding(self):
        """Total pendanaan masuk (Sum Amount)"""
        from funding.models import Funding
        # Hanya hitung funding yang statusnya 'active' (uang benar-benar masuk)
        return Funding.objects.filter(status='active').aggregate(Sum('amount'))['amount__sum'] or 0

    def total_revenue(self):
        """Total Penjualan / Omzet"""
        from sales.models import Sale
        return Sale.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0

    def total_expense(self):
        """Total Pengeluaran"""
        from expense.models import Expense
        return Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0

    def total_yield(self):
        """Total Bagi Hasil yang SUDAH sampai ke tangan user"""
        from profit_distribution.models import ProfitDistributionItem
        return ProfitDistributionItem.objects.aggregate(Sum('amount'))['amount__sum'] or 0

    def total_cash_on_hand(self):
        """
        Rumus Dana Global (Cash on Hand):
        (Total Uang Masuk) - (Total Uang Keluar REAL)
        
        LOGIKA BENAR SESUAI REQUEST:
        Kita HANYA mengurangi uang yang tercatat di 'ProfitDistributionItem'.
        
        Contoh Kasus:
        - Input Admin: 5 Juta
        - Potongan Landowner: 500rb (Tercatat di Item)
        - Jatah Investor (hanya yg beli saham): 100rb (Tercatat di Item)
        - Sisa (Retained): 4.4 Juta (TIDAK ADA di Item)
        
        Perhitungan:
        Pengurang = 500rb + 100rb = 600rb.
        
        Hasilnya: Saldo kas hanya berkurang 600rb. 
        Sisa 4.4 Juta OTOMATIS tetap ada di Dana Global karena tidak kita kurangi.
        """
        from funding.models import Funding
        from expense.models import Expense
        from sales.models import Sale
        # [FIX] Gunakan Item, bukan Header
        from profit_distribution.models import ProfitDistributionItem

        # 1. PEMASUKAN
        funding_in = Funding.objects.filter(status='active').aggregate(Sum('amount'))['amount__sum'] or 0
        sales_in = Sale.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
        total_in = funding_in + sales_in

        # 2. PENGELUARAN
        expense_out = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # [FIX] Hanya hitung uang yang benar-benar dibagikan (Landowner + Investor Aktif)
        dividend_out_real = ProfitDistributionItem.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        
        total_out = expense_out + dividend_out_real
        
        # 3. SALDO AKHIR
        return total_in - total_out

    def shares_sold(self):
        from funding.models import Funding
        return Funding.objects.filter(source_type='investor', status='active').aggregate(Sum('shares'))['shares__sum'] or 0
    
    def shares_available(self):
        return self.total_system_shares - self.shares_sold()