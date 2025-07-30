from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from asset.models import Asset
from funding.models import Funding
from production.models import Production
from ownership.models import Ownership
from investor.models import Investor

# Create your views here.
@api_view (['GET'])
@permission_classes([IsAuthenticated])
def Dashboard(request):
    total_assets = Asset.objects.count()
    total_funding = Funding.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_yield =Production.objects.aggregate(total=Sum('total_value'))['total'] or 0
    total_units = Ownership.objects.aggregate(total_units=Sum('units'))['total_units'] or 0
    ownership_list=[]
    if total_units:
        investor_aggregate = (
            Ownership.objects\
            .values('investor__user__username')\
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
        "total_funding": total_funding,
        "total_yield": total_yield,
        "ownership_precentage": ownership_list
    }

    return Response(data)