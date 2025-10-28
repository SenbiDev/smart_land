# File: reporting/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, F, DecimalField, Q, Count
from django.db.models.functions import ExtractMonth, ExtractYear
from funding.models import Funding
from expense.models import Expense
from production.models import Production
from ownership.models import Ownership 
from investor.models import Investor
from decimal import Decimal

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def laporan_keuangan(request):
    user = request.user
    total_dana = 0
    total_pengeluaran = 0
    total_yield = 0

    if user.role == 'Investor':
        try:
            investor = user.investor
            investor_ownerships = Ownership.objects.filter(investor=investor)
            asset_ids = investor_ownerships.values_list('asset_id', flat=True).distinct()
            funding_ids = investor_ownerships.values_list('funding_id', flat=True).distinct()

            total_dana = Funding.objects.filter(id__in=funding_ids).aggregate(total=Sum('amount'))['total'] or 0
            total_pengeluaran = Expense.objects.filter(
                Q(asset_id__in=asset_ids) | Q(funding_id__in=funding_ids)
            ).distinct().aggregate(total=Sum('amount'))['total'] or 0
            total_yield = Production.objects.filter(asset_id__in=asset_ids).aggregate(
                total=Sum(F('quantity') * F('unit_price'), output_field=DecimalField())
            )['total'] or 0
        except Investor.DoesNotExist:
            return Response({"error": "Profil investor tidak ditemukan."}, status=404)
    else:
        total_dana = Funding.objects.aggregate(total=Sum('amount'))['total'] or 0
        total_pengeluaran = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
        total_yield = Production.objects.aggregate(
            total=Sum(F('quantity') * F('unit_price'), output_field=DecimalField())
        )['total'] or 0

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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pengeluaran_per_kategori(request):
    user = request.user
    
    if user.role == 'Investor':
        try:
            investor = user.investor
            investor_ownerships = Ownership.objects.filter(investor=investor)
            asset_ids = investor_ownerships.values_list('asset_id', flat=True).distinct()
            funding_ids = investor_ownerships.values_list('funding_id', flat=True).distinct()
            expenses = Expense.objects.filter(
                Q(asset_id__in=asset_ids) | Q(funding_id__in=funding_ids)
            ).distinct()
        except Investor.DoesNotExist:
            return Response({"error": "Profil investor tidak ditemukan."}, status=404)
    else:
        expenses = Expense.objects.all()
    
    category_data = expenses.values('category').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    result = [
        {"category": item['category'] or 'Lainnya', "amount": float(item['total'])}
        for item in category_data
    ]
    return Response(result, status=http_status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_pengeluaran(request):
    user = request.user
    
    if user.role == 'Investor':
        try:
            investor = user.investor
            investor_ownerships = Ownership.objects.filter(investor=investor)
            asset_ids = investor_ownerships.values_list('asset_id', flat=True).distinct()
            funding_ids = investor_ownerships.values_list('funding_id', flat=True).distinct()
            expenses = Expense.objects.filter(
                Q(asset_id__in=asset_ids) | Q(funding_id__in=funding_ids)
            ).distinct()
        except Investor.DoesNotExist:
            return Response({"error": "Profil investor tidak ditemukan."}, status=404)
    else:
        expenses = Expense.objects.all()
    
    top_expenses = expenses.select_related('asset_id', 'funding_id').order_by('-amount')[:5]
    
    result = [
        {
            "id": exp.id,
            "amount": float(exp.amount),
            "description": exp.description,
            "asset": exp.asset_id.name if exp.asset_id else None,
            "funding": f"Funding #{exp.funding_id.id}" if exp.funding_id else None,
            "date": exp.date.isoformat(),
            "category": exp.category
        }
        for exp in top_expenses
    ]
    return Response(result, status=http_status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pendapatan_vs_pengeluaran(request):
    user = request.user
    
    if user.role == 'Investor':
        try:
            investor = user.investor
            investor_ownerships = Ownership.objects.filter(investor=investor)
            asset_ids = investor_ownerships.values_list('asset_id', flat=True).distinct()
            funding_ids = investor_ownerships.values_list('funding_id', flat=True).distinct()
            productions = Production.objects.filter(asset_id__in=asset_ids)
            expenses = Expense.objects.filter(
                Q(asset_id__in=asset_ids) | Q(funding_id__in=funding_ids)
            ).distinct()
        except Investor.DoesNotExist:
            return Response({"error": "Profil investor tidak ditemukan."}, status=404)
    else:
        productions = Production.objects.all()
        expenses = Expense.objects.all()
    
    # PERBAIKAN: Gunakan annotate untuk grouping
    from django.db.models.functions import TruncMonth
    from datetime import datetime
    
    # Group production by month
    monthly_income = {}
    for prod in productions.select_related('asset'):
        month_key = prod.date.strftime('%Y-%m')
        total_value = float(prod.quantity) * float(prod.unit_price)
        if month_key not in monthly_income:
            monthly_income[month_key] = 0
        monthly_income[month_key] += total_value
    
    # Group expenses by month
    monthly_expense = {}
    for exp in expenses:
        month_key = exp.date.strftime('%Y-%m')
        if month_key not in monthly_expense:
            monthly_expense[month_key] = 0
        monthly_expense[month_key] += float(exp.amount)
    
    # Combine all months
    all_months = sorted(set(list(monthly_income.keys()) + list(monthly_expense.keys())))
    
    # Take last 6 months
    result = []
    for month in all_months[-6:]:
        result.append({
            "month": month,
            "income": monthly_income.get(month, 0),
            "expense": monthly_expense.get(month, 0)
        })
    
    return Response(result, status=http_status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ringkasan_kuartal(request):
    user = request.user
    
    if user.role == 'Investor':
        try:
            investor = user.investor
            investor_ownerships = Ownership.objects.filter(investor=investor)
            asset_ids = investor_ownerships.values_list('asset_id', flat=True).distinct()
            funding_ids = investor_ownerships.values_list('funding_id', flat=True).distinct()
            fundings = Funding.objects.filter(id__in=funding_ids)
            expenses = Expense.objects.filter(
                Q(asset_id__in=asset_ids) | Q(funding_id__in=funding_ids)
            ).distinct()
            productions = Production.objects.filter(asset_id__in=asset_ids)
        except Investor.DoesNotExist:
            return Response({"error": "Profil investor tidak ditemukan."}, status=404)
    else:
        fundings = Funding.objects.all()
        expenses = Expense.objects.all()
        productions = Production.objects.all()
    
    total_funding = float(fundings.aggregate(total=Sum('amount'))['total'] or 0)
    total_expense = float(expenses.aggregate(total=Sum('amount'))['total'] or 0)
    total_yield = float(productions.aggregate(
        total=Sum(F('quantity') * F('unit_price'), output_field=DecimalField())
    )['total'] or 0)
    
    quarters = ['Q1-25', 'Q2-25', 'Q3-25', 'Q4-25']
    result = []
    for q in quarters:
        funding_q = total_funding / 4
        expense_q = total_expense / 4
        yield_q = total_yield / 4
        result.append({
            "quarter": q,
            "funding": funding_q,
            "expense": expense_q,
            "yield": yield_q,
            "net_profit": yield_q - expense_q
        })
    
    return Response(result, status=http_status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def yield_report(request):
    user = request.user
    
    if user.role == 'Investor':
        try:
            investor = user.investor
            investor_ownerships = Ownership.objects.filter(investor=investor)
            asset_ids = investor_ownerships.values_list('asset_id', flat=True).distinct()
            productions = Production.objects.filter(asset_id__in=asset_ids)
            funding_ids = investor_ownerships.values_list('funding_id', flat=True).distinct()
            total_investasi = Funding.objects.filter(id__in=funding_ids).aggregate(total=Sum('amount'))['total'] or 0
            expenses = Expense.objects.filter(
                Q(asset_id__in=asset_ids) | Q(funding_id__in=funding_ids)
            ).distinct()
        except Investor.DoesNotExist:
            return Response({"error": "Profil investor tidak ditemukan."}, status=404)
    else:
        productions = Production.objects.all()
        total_investasi = Funding.objects.aggregate(total=Sum('amount'))['total'] or 0
        expenses = Expense.objects.all()
    
    total_yield = productions.aggregate(
        total=Sum(F('quantity') * F('unit_price'), output_field=DecimalField())
    )['total'] or 0
    
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    hasil_bersih = float(total_yield) - float(total_expense)
    margin_laba = (hasil_bersih / float(total_yield) * 100) if total_yield > 0 else 0
    
    return Response({
        "total_investasi": float(total_investasi),
        "total_hasil_produksi": float(total_yield),
        "hasil_bersih": hasil_bersih,
        "margin_laba": round(margin_laba, 1)
    }, status=http_status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def investor_yield(request):
    user = request.user
    
    if user.role != 'Investor':
        ownerships = Ownership.objects.select_related('investor', 'funding').all()
    else:
        try:
            investor = user.investor
            ownerships = Ownership.objects.filter(investor=investor)
        except Investor.DoesNotExist:
            return Response({"error": "Profil investor tidak ditemukan."}, status=404)
    
    investor_data = {}
    for own in ownerships:
        investor_name = own.investor.user.username
        if investor_name not in investor_data:
            investor_data[investor_name] = {
                "total_funding": 0,
                "total_yield": 0
            }
        
        investor_data[investor_name]["total_funding"] += float(own.funding.amount * Decimal(own.ownership_percentage) / 100)
        
        asset_yield = Production.objects.filter(asset=own.asset).aggregate(
            total=Sum(F('quantity') * F('unit_price'), output_field=DecimalField())
        )['total'] or 0
        
        investor_data[investor_name]["total_yield"] += float(asset_yield * Decimal(own.ownership_percentage) / 100)
    
    result = []
    for name, data in investor_data.items():
        yield_percent = (data["total_yield"] / data["total_funding"] * 100) if data["total_funding"] > 0 else 0
        result.append({
            "investor": name,
            "total_funding": data["total_funding"],
            "total_yield": data["total_yield"],
            "yield_percent": round(yield_percent, 1)
        })
    
    return Response(result, status=http_status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def funding_progress(request):
    user = request.user
    
    if user.role == 'Investor':
        try:
            investor = user.investor
            investor_ownerships = Ownership.objects.filter(investor=investor)
            funding_ids = investor_ownerships.values_list('funding_id', flat=True).distinct()
            fundings = Funding.objects.filter(id__in=funding_ids)
            asset_ids = investor_ownerships.values_list('asset_id', flat=True).distinct()
            expenses = Expense.objects.filter(
                Q(asset_id__in=asset_ids) | Q(funding_id__in=funding_ids)
            ).distinct()
        except Investor.DoesNotExist:
            return Response({"error": "Profil investor tidak ditemukan."}, status=404)
    else:
        fundings = Funding.objects.all()
        expenses = Expense.objects.all()
    
    total_funding = fundings.aggregate(total=Sum('amount'))['total'] or 0
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    total = float(total_funding) + float(total_expense)
    funding_percent = (float(total_funding) / total * 100) if total > 0 else 0
    expense_percent = (float(total_expense) / total * 100) if total > 0 else 0
    
    return Response({
        "funding": {
            "amount": float(total_funding),
            "percent": round(funding_percent, 1)
        },
        "expense": {
            "amount": float(total_expense),
            "percent": round(expense_percent, 1)
        }
    }, status=http_status.HTTP_200_OK)