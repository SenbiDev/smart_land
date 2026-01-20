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

    # --- FUNGSI HITUNG OTOMATIS ---
    
    def total_asset_value(self):
        from asset.models import Asset
        total = Asset.objects.aggregate(Sum('value'))['value__sum'] or 0
        return total # Return angka raw, biar frontend yang format

    def total_cash_on_hand(self):
        from funding.models import Funding
        from expense.models import Expense
        from sales.models import Sale
        from profit_distribution.models import ProfitDistributionItem

        # 1. Total Pemasukan (Funding + Sales)
        investor_money = Funding.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        sales_revenue = Sale.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
        total_in = investor_money + sales_revenue

        # 2. Total Pengeluaran (Belanja/Gaji)
        total_expense = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # 3. Total Bagi Hasil (REAL PAYOUT)
        # Kita hitung jumlah detail item yang dibagikan ke investor/landowner
        total_payout_real = ProfitDistributionItem.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # 4. Rumus Saldo Akhir
        # Saldo = Masuk - (Keluar Belanja + Keluar Bagi Hasil)
        # *Retained Earnings otomatis tersisa disini karena tidak dikurangi*
        saldo = total_in - total_expense - total_payout_real
        
        return saldo # Return angka raw

    def shares_sold(self):
        from funding.models import Funding
        return Funding.objects.filter(source_type='investor').aggregate(Sum('shares'))['shares__sum'] or 0
    
    def shares_available(self):
        from funding.models import Funding
        sold = Funding.objects.filter(source_type='investor').aggregate(Sum('shares'))['shares__sum'] or 0
        return self.total_system_shares - sold