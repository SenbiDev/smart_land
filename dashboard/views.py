from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum

# Import model-model baru yang sudah kita buat
from asset.models import Asset
from funding.models import Funding
from expense.models import Expense
from sales.models import Sale
from profit_distribution.models import ProfitDistribution

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Dashboard(request):
    # 1. Total Nilai Aset (Jumlah Aset Fisik)
    total_assets = Asset.objects.count()
    
    # 2. Total Pendanaan Masuk (Investor + Donasi)
    total_funding = Funding.objects.aggregate(total=Sum('amount'))['total'] or 0
    
    # 3. Total Penjualan (Revenue / Uang Masuk Operasional)
    total_sales = Sale.objects.aggregate(total=Sum('total_price'))['total'] or 0
    
    # 4. Total Pengeluaran (Expense / Uang Keluar)
    total_expense = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    
    # 5. Estimasi Laba Bersih (Cashflow saat ini)
    net_profit = float(total_sales) - float(total_expense)
    
    # 6. Total Bagi Hasil yang sudah dibagikan
    total_distributed = ProfitDistribution.objects.filter(status='distributed').aggregate(total=Sum('total_distributed'))['total'] or 0

    data = {
        "summary": {
            "total_assets": total_assets,
            "total_funding": float(total_funding),
            "total_revenue": float(total_sales),
            "total_expense": float(total_expense),
            "net_profit": net_profit,
            "total_distributed": float(total_distributed)
        },
        # Info tambahan untuk grafik sederhana di FE (Opsional)
        "recent_sales": Sale.objects.order_by('-date')[:5].values('product_name', 'total_price', 'date'),
        "recent_expenses": Expense.objects.order_by('-date')[:5].values('title', 'amount', 'date')
    }

    return Response(data)