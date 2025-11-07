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

    # --- Filter data berdasarkan Role ---
    if user.role == 'Investor':
        try:
            investor = user.investor
            investor_ownerships = Ownership.objects.filter(investor=investor)
            asset_ids = investor_ownerships.values_list('asset_id', flat=True).distinct()
            
            # Statistics
            total_assets = Asset.objects.filter(id__in=asset_ids).count()
            total_funding = investor_ownerships.aggregate(total=Sum('funding__amount'))['total'] or 0
            total_yield = Production.objects.filter(asset_id__in=asset_ids).aggregate(total=Sum('total_value'))['total'] or 0
            
            # PERBAIKAN: Ownership list menampilkan per-aset dengan persentase investor
            ownership_list = list(
                investor_ownerships.values('asset__name')
                .annotate(
                    units=Sum('units'),
                    percentage=Sum('ownership_percentage')
                )
                .order_by('-percentage')
            )
            
            # Format: "Aset X (50 units) - 25%"
            ownership_list = [
                {
                    "name": f"{o['asset__name']} ({int(o['units'])} units)", 
                    "percentage": float(o['percentage'])
                }
                for o in ownership_list
            ]

        except Investor.DoesNotExist:
            return Response({"error": "Profil investor tidak ditemukan."}, status=404)
            
    else:
        # Admin/Superadmin/Operator/Viewer: Data global
        total_assets = Asset.objects.count()
        total_funding = Funding.objects.aggregate(total=Sum('amount'))['total'] or 0
        total_yield = Production.objects.aggregate(total=Sum('total_value'))['total'] or 0
        
        # Ownership list: Tampilkan per-investor (global view)
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
    
    data = {
        "total_assets": total_assets,
        "total_funding": float(total_funding),
        "total_yield": float(total_yield),
        "ownership_percentage": ownership_list
    }

    return Response(data)