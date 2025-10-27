# File: senbidev/smart_land/smart_land-faiz/reporting/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, F, DecimalField, Q # Impor Q
from funding.models import Funding
from expense.models import Expense
from production.models import Production
# Impor model untuk filter
from ownership.models import Ownership 
from investor.models import Investor

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def laporan_keuangan(request):
    user = request.user

    total_dana = 0
    total_pengeluaran = 0
    total_yield = 0

    # --- POIN 4: Filter data berdasarkan Role ---
    if user.role == 'Investor':
        try:
            investor = user.investor
            investor_ownerships = Ownership.objects.filter(investor=investor)
            
            asset_ids = investor_ownerships.values_list('asset_id', flat=True).distinct()
            funding_ids = investor_ownerships.values_list('funding_id', flat=True).distinct()

            # Total dana dari pendanaan yang terkait DENGAN investor ini
            total_dana = Funding.objects.filter(id__in=funding_ids).aggregate(total=Sum('amount'))['total'] or 0
            
            # Total pengeluaran dari aset ATAU pendanaan yang terkait
            total_pengeluaran = Expense.objects.filter(
                Q(asset_id__in=asset_ids) | Q(funding_id__in=funding_ids)
            ).distinct().aggregate(total=Sum('amount'))['total'] or 0
            
            # Total yield dari aset yang terkait
            total_yield = Production.objects.filter(asset_id__in=asset_ids).aggregate(
                total=Sum(F('quantity') * F('unit_price'), output_field=DecimalField())
            )['total'] or 0

        except Investor.DoesNotExist:
            return Response({"error": "Profil investor tidak ditemukan."}, status=404)
    
    else:
        # Perilaku lama untuk Admin, Superadmin, Operator, dan Viewer (data global)
        total_dana = Funding.objects.aggregate(total=Sum('amount'))['total'] or 0
        total_pengeluaran = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
        total_yield = Production.objects.aggregate(
            total=Sum(F('quantity') * F('unit_price'), output_field=DecimalField())
        )['total'] or 0
    # ------------------------------------------

    laba_rugi = total_yield - total_pengeluaran
    sisa_dana = total_dana - total_pengeluaran

    if laba_rugi > 0:
        status_keuangan = "Laba"
    elif laba_rugi < 0:
        status_keuangan = "Rugi"
    else:
        status_keuangan = "Impas"

    data = {
        "ringkasan_dana": {
            "total_dana_masuk": float(total_dana),
            "total_pengeluaran": float(total_pengeluaran),
            "sisa_dana": float(sisa_dana)
        },
        "total_yield": float(total_yield),
        "laba_rugi": {
            "Jumlah": float(laba_rugi),
            "Status": status_keuangan
        }
    }

    return Response(data, status=http_status.HTTP_200_OK)