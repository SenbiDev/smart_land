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

    if user.role and user.role.name == 'Investor': 
        try:
            investor = user.investor
            investor_ownerships = Ownership.objects.filter(investor=investor)
            
            asset_ids = investor_ownerships.filter(asset__isnull=False).values_list('asset_id', flat=True).distinct()
            total_assets = Asset.objects.filter(id__in=asset_ids).count()
            
            total_funding = investor_ownerships.aggregate(total=Sum('funding__amount'))['total'] or 0
            
            total_yield = DistributionDetail.objects.filter(investor=investor).aggregate(total=Sum('amount_received'))['total'] or 0
            
            ownership_qs = investor_ownerships.select_related('asset').order_by('-ownership_percentage')
            
            for o in ownership_qs:
                pct = float(o.ownership_percentage) if o.ownership_percentage else 0.0
                asset_name = o.asset.name if o.asset else "Dana Mengendap (Cash)"
                
                ownership_list.append({
                    "name": asset_name, 
                    "units": o.units,
                    "percentage": pct
                })

        except Investor.DoesNotExist:
            pass
            
    else:
        total_assets = Asset.objects.count()
        
        total_funding = Funding.objects.aggregate(total=Sum('amount'))['total'] or 0
        
        total_yield = Production.objects.aggregate(total=Sum('total_value'))['total'] or 0
        
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