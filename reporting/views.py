from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, F, DecimalField
from funding.models import Funding
from expense.models import Expense
from production.models import Production

#Create your views here
@api_view(['GET'])
def laporan_keuangan(request):
    total_dana = Funding.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_pengeluaran = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_yield = Production.objects.aggregate(total=Sum(F('quantity') * F('unit_price'), output_field=DecimalField()))['total'] or 0
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

    return Response(data, status=status.HTTP_200_OK)
