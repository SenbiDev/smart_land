from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from asset.models import Asset
from funding.models import Funding
from production.models import Production
from ownership.models import Ownership
from investor.models import Investor
from distribution_detail.models import DistributionDetail 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Dashboard(request):
    user = request.user
    
    total_assets = 0
    total_funding = 0
    total_yield = 0
    ownership_list = []

    # --- Skenario: Investor (Privasi Data Pribadi) ---
    if user.role and user.role.name == 'Investor': 
        try:
            investor = user.investor
            investor_ownerships = Ownership.objects.filter(investor=investor)
            asset_ids = investor_ownerships.values_list('asset_id', flat=True).distinct()
            
            # 1. Total Aset yang didanai oleh investor ini
            total_assets = Asset.objects.filter(id__in=asset_ids).count()
            
            # 2. Total Investasi (Uang yang dikeluarkan investor ini saja)
            # Menghitung berdasarkan proporsi kepemilikan di funding jika perlu, 
            # atau total amount dari Ownership record jika ada field amount.
            # Fallback: Ambil total unit * harga per unit (jika ada) atau sum funding terkait.
            # Di sini kita gunakan sum amount dari Funding yang terhubung ke Ownership user.
            total_funding = investor_ownerships.aggregate(total=Sum('funding__amount'))['total'] or 0
            
            # 3. Total Yield (Uang Bersih / Dividen yang diterima Investor)
            # Menggunakan DistributionDetail agar akurat sesuai uang masuk ke kantong investor
            total_yield = DistributionDetail.objects.filter(investor=investor).aggregate(total=Sum('amount_received'))['total'] or 0
            
            # 4. List Kepemilikan (Portofolio)
            ownership_qs = investor_ownerships.select_related('asset').order_by('-ownership_percentage')
            
            for o in ownership_qs:
                pct = float(o.ownership_percentage) if o.ownership_percentage else 0.0
                ownership_list.append({
                    "name": o.asset.name, 
                    "units": o.units,
                    "percentage": pct
                })

        except Investor.DoesNotExist:
            # Jika user punya role Investor tapi belum ada data di tabel Investor
            pass
            
    # --- Skenario: Admin/Superadmin/Viewer/Operator (Data Global Platform) ---
    else:
        # 1. Total Aset kelolaan platform
        total_assets = Asset.objects.count()
        
        # 2. Total Dana Masuk (Akumulasi semua funding)
        total_funding = Funding.objects.aggregate(total=Sum('amount'))['total'] or 0
        
        # 3. Total Nilai Produksi (Omzet Kotor Platform)
        # Admin melihat performa aset, bukan dividen bersih
        total_yield = Production.objects.aggregate(total=Sum('total_value'))['total'] or 0
        
        # 4. Distribusi Kepemilikan Global (Top Investors)
        # Menampilkan siapa saja pemegang saham terbesar di platform
        top_ownerships = Ownership.objects.values('investor__user__username').annotate(
            total_pct=Sum('ownership_percentage')
        ).order_by('-total_pct')[:5]

        for entry in top_ownerships:
            ownership_list.append({
                "name": entry['investor__user__username'],
                "percentage": float(entry['total_pct'])
            })
    
    data = {
        "total_assets": total_assets,
        "total_funding": float(total_funding),
        "total_yield": float(total_yield),
        "ownership_percentage": ownership_list
    }

    return Response(data)