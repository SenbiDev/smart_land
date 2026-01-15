from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum, Count

# Import Model dari app lain
from asset.models import Asset
from funding.models import Funding
from expense.models import Expense
from sales.models import Sale
from production.models import Production

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny] 

    def list(self, request):
        # 1. Hitung Total Aset
        total_assets = Asset.objects.count()
        total_asset_value = Asset.objects.aggregate(sum_val=Sum('value'))['sum_val'] or 0

        # 2. Hitung Keuangan (Cashflow)
        total_funding = Funding.objects.aggregate(sum_val=Sum('amount'))['sum_val'] or 0
        total_revenue = Sale.objects.aggregate(sum_val=Sum('total_price'))['sum_val'] or 0
        total_expense = Expense.objects.aggregate(sum_val=Sum('amount'))['sum_val'] or 0
        
        # Saldo Kas
        total_cash_on_hand = (total_funding + total_revenue) - total_expense

        # 3. Hitung Produksi
        # Gunakan Revenue Penjualan sebagai representasi Nilai Yield sementara
        total_yield = total_revenue 

        # 4. Hitung Statistik Saham
        SHARE_PRICE = 1000000
        shares_sold = int(total_funding / SHARE_PRICE) 
        shares_available = 1000 - shares_sold 

        data = {
            "total_assets": total_assets,
            "total_asset_value": total_asset_value,
            "total_funding": total_funding,
            "total_revenue": total_revenue, # Tambahan untuk Frontend
            "total_expense": total_expense, # Tambahan untuk Frontend
            "total_cash_on_hand": total_cash_on_hand,
            "total_yield": total_yield,
            "shares_sold": shares_sold,
            "shares_available": shares_available,
            "ownership_percentage": [], 
        }

        return Response(data)