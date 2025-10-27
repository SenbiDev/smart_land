# File: senbidev/smart_land/smart_land-faiz/dashboard/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from asset.models import Asset
from funding.models import Funding
from production.models import Production
from ownership.models import Ownership
from investor.models import Investor

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Dashboard(request):
    user = request.user
    
    total_assets = 0
    total_funding = 0
    total_yield = 0
    ownership_list = []

    # --- POIN 4: Filter data berdasarkan Role ---
    if user.role == 'Investor':
        try:
            # Dapatkan profil investor dari user yang login
            investor = user.investor
            
            # 1. Dapatkan semua kepemilikan investor
            investor_ownerships = Ownership.objects.filter(investor=investor)
            
            # 2. Dapatkan ID unik Aset & Pendanaan dari kepemilikan tsb
            asset_ids = investor_ownerships.values_list('asset_id', flat=True).distinct()
            
            # 3. Hitung statistik HANYA berdasarkan aset/pendanaan terkait
            total_assets = Asset.objects.filter(id__in=asset_ids).count()
            
            # Total pendanaan dari investor ini (lebih akurat)
            total_funding = investor_ownerships.aggregate(total=Sum('funding__amount'))['total'] or 0
            
            # Total yield dari aset yang dia miliki
            total_yield = Production.objects.filter(asset_id__in=asset_ids).aggregate(total=Sum('total_value'))['total'] or 0
            
            # 4. Hitung persentase kepemilikan (hanya tampilkan data investor ini per aset)
            ownership_list = list(investor_ownerships.values('asset__name').annotate(
                units=Sum('units'),
                percentage=Sum('ownership_percentage') # Ambil persentase yang sudah dihitung
            ).order_by('-percentage'))
            
            # Format ulang agar konsisten (opsional, tapi bagus)
            ownership_list = [
                {"name": f"{o['asset__name']} ({o['units']} units)", "percentage": o['percentage']}
                for o in ownership_list
            ]

        except Investor.DoesNotExist:
            # Handle jika user ber-role Investor tapi profil Investor-nya belum dibuat
            return Response({"error": "Profil investor tidak ditemukan."}, status=404)
            
    else:
        # Perilaku lama untuk Admin, Superadmin, Operator, dan Viewer (data global)
        total_assets = Asset.objects.count()
        total_funding = Funding.objects.aggregate(total=Sum('amount'))['total'] or 0
        total_yield = Production.objects.aggregate(total=Sum('total_value'))['total'] or 0
        total_units = Ownership.objects.aggregate(total_units=Sum('units'))['total_units'] or 0
        
        if total_units:
            investor_aggregate = (
                Ownership.objects
                .values('investor__user__username')
                .annotate(total_units=Sum('units'))
            )
            for entry in investor_aggregate:
                name = entry['investor__user__username']
                percentage = round((entry["total_units"] / total_units) * 100, 2)
                ownership_list.append({
                    "name": name,
                    "percentage": percentage
                })
    # ------------------------------------------
    
    data = {
        "total_assets": total_assets,
        "total_funding": total_funding,
        "total_yield": total_yield,
        "ownership_percentage": ownership_list
    }

    return Response(data)