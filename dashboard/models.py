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

    # --- FUNGSI HITUNG OTOMATIS (LOGIKA BENAR) ---
    
    def total_asset_value(self):
        from asset.models import Asset
        total = Asset.objects.aggregate(Sum('value'))['value__sum'] or 0
        return f"Rp {total:,.2f}"

    def total_cash_on_hand(self):
        from funding.models import Funding
        from expense.models import Expense
        from sales.models import Sale
        from profit_distribution.models import ProfitDistribution

        # 1. Total Pemasukan
        investor_money = Funding.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        sales_revenue = Sale.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
        total_in = investor_money + sales_revenue

        # 2. Total Pengeluaran (Belanja/Gaji)
        total_expense = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # 3. Total Bagi Hasil (HANYA YANG BENAR-BENAR DITRANSFER)
        # Kita jumlahkan jatah Landowner + Jatah Investor Real saja.
        # Sisa dana (Retained Earnings) tidak kita hitung sebagai pengeluaran, jadi tetap di saldo.
        dist_aggregates = ProfitDistribution.objects.aggregate(
            real_lo=Sum('landowner_total_amount'),
            real_inv=Sum('investor_total_amount')
        )
        
        payout_landowner = dist_aggregates['real_lo'] or 0
        payout_investor = dist_aggregates['real_inv'] or 0
        
        total_payout_real = payout_landowner + payout_investor
        
        # 4. Rumus Saldo Akhir
        saldo = total_in - total_expense - total_payout_real
        
        return f"Rp {saldo:,.2f}"

    def shares_sold(self):
        from funding.models import Funding
        sold = Funding.objects.filter(source_type='investor').aggregate(Sum('shares'))['shares__sum'] or 0
        return f"{sold} Lembar"
    
    def shares_available(self):
        from funding.models import Funding
        sold = Funding.objects.filter(source_type='investor').aggregate(Sum('shares'))['shares__sum'] or 0
        sisa = self.total_system_shares - sold
        return f"{sisa} Lembar"