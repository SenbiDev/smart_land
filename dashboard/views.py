from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from asset.models import Asset
from funding.models import Funding
from production.models import Production
from ownership.models import Ownership
from investor.models import Investor
# [FIX] Import model DistributionDetail untuk mengambil nilai bagi hasil bersih
from distribution_detail.models import DistributionDetail 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Dashboard(request):
    user = request.user
    
    total_assets = 0
    total_funding = 0
    total_yield = 0
    ownership_list = []

    # --- Filter data berdasarkan Role ---
    if request.user.role and request.user.role.name == 'Investor': # Pastikan cek role aman
        try:
            investor = user.investor
            investor_ownerships = Ownership.objects.filter(investor=investor)
            asset_ids = investor_ownerships.values_list('asset_id', flat=True).distinct()
            
            # 1. Total Aset yang didanai
            total_assets = Asset.objects.filter(id__in=asset_ids).count()
            
            # 2. Total Investasi (Uang yang dikeluarkan)
            total_funding = investor_ownerships.aggregate(total=Sum('funding__amount'))['total'] or 0
            
            # 3. [PERBAIKAN] Total Yield (Uang Bersih yang diterima Investor)
            # Dulu: Production (Omzet Kotor 60jt) -> SALAH
            # Sekarang: DistributionDetail (Net 51jt) -> BENAR
            total_yield = DistributionDetail.objects.filter(investor=investor).aggregate(total=Sum('amount_received'))['total'] or 0
            
            # 4. List Kepemilikan
            ownership_list = list(
                investor_ownerships.values('asset__name')
                .annotate(
                    units=Sum('units'),
                    percentage=Sum('ownership_percentage') # Asumsi field ini ada di model Ownership
                )
                .order_by('-percentage')
            )
            
            # Formatting List
            formatted_ownership = []
            for o in ownership_list:
                # Handle jika percentage null
                pct = float(o['percentage']) if o['percentage'] else 0.0
                formatted_ownership.append({
                    "name": f"{o['asset__name']} ({int(o['units'])} units)", 
                    "percentage": pct
                })
            ownership_list = formatted_ownership

        except Investor.DoesNotExist:
            return Response({"error": "Profil investor tidak ditemukan."}, status=404)
            
    else:
        # Admin/Superadmin/Operator/Viewer: Data Global (Omzet Kotor Platform)
        total_assets = Asset.objects.count()
        
        # Total Dana Masuk ke Platform
        total_funding = Funding.objects.aggregate(total=Sum('amount'))['total'] or 0
        
        # Total Nilai Produksi (Omzet Kotor Platform) - Tetap 60jt untuk Admin karena ini performa aset
        total_yield = Production.objects.aggregate(total=Sum('total_value'))['total'] or 0
        
        # Ownership list: Per-investor (Global View)
        total_units = Ownership.objects.aggregate(total_units=Sum('units'))['total_units'] or 0
        
        if total_units:
            investor_aggregate = (
                Ownership.objects
                .values('investor__user__username')
                .annotate(total_units=Sum('units'))
            )
            for entry in investor_aggregate:
                name = entry['investor__user__username']
                # Hitung persentase kepemilikan global
                percentage = round((entry["total_units"] / total_units) * 100, 2)
                ownership_list.append({
                    "name": name,
                    "percentage": percentage
                })
    
    data = {
        "total_assets": total_assets,
        "total_funding": float(total_funding),
        "total_yield": float(total_yield),
        "ownership_percentage": ownership_list
    }

    return Response(data)