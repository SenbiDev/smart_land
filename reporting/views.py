from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, F, DecimalField, Q
from django.db.models.functions import Coalesce, TruncMonth, ExtractQuarter, ExtractYear
from decimal import Decimal
from collections import defaultdict
import datetime

# Import semua model yang diperlukan
from funding.models import Funding
from expense.models import Expense
from production.models import Production
from ownership.models import Ownership 
from investor.models import Investor
from project.models import Project

# =================================================================================
# FUNGSI HELPER UTAMA: FILTERING & DATA SCOPING
# =================================================================================

def get_filtered_querysets(request):
    """
    Satu fungsi pusat untuk mendapatkan queryset yang SUDAH DIFILTER.
    Perbaikan: Menangani field lookup 'project_id' vs 'project' dengan tepat.
    """
    user = request.user
    
    # Ambil query params
    asset_id = request.GET.get('asset')
    project_id = request.GET.get('project')
    period = request.GET.get('period') # Format 'YYYY-MM', 'YYYY-Qn', atau 'YYYY'

    # Queryset awal (All Data) - Gunakan select_related untuk optimasi
    fundings_qs = Funding.objects.all()
    # [FIX] Expense menggunakan 'project_id' sesuai definisi model
    expenses_qs = Expense.objects.select_related('project_id__asset').all() 
    productions_qs = Production.objects.select_related('asset').all()
    ownerships_qs = Ownership.objects.select_related('investor', 'asset').all()

    # --- 1. FILTER BERDASARKAN ROLE (SECURITY & PRIVACY) ---
    if user.role and user.role.name == 'Investor':
        try:
            investor = user.investor
            # Ambil semua aset yang dimiliki investor ini
            investor_ownerships = Ownership.objects.filter(investor=investor)
            owned_asset_ids = investor_ownerships.values_list('asset_id', flat=True).distinct()
            
            # Validasi: Jika investor tidak punya aset, return kosong
            if not owned_asset_ids:
                return (Funding.objects.none(), Expense.objects.none(), 
                        Production.objects.none(), Ownership.objects.none())

            # Filter Funding: Dana masuk ke Proyek di Aset milik investor
            # Funding model menggunakan relasi 'project'
            fundings_qs = fundings_qs.filter(project__asset_id__in=owned_asset_ids)
            
            # [CRITICAL FIX] Filter Expense: Pengeluaran dari Proyek di Aset milik investor
            # Expense model menggunakan field 'project_id', BUKAN 'project'
            expenses_qs = expenses_qs.filter(project_id__asset_id__in=owned_asset_ids)
            
            # Filter Production: Hasil panen dari Aset milik investor
            productions_qs = productions_qs.filter(asset_id__in=owned_asset_ids)
            
            # Filter Ownership: HANYA data kepemilikan DIRI SENDIRI
            ownerships_qs = ownerships_qs.filter(investor=investor)
            
        except Investor.DoesNotExist:
            return (Funding.objects.none(), Expense.objects.none(), 
                    Production.objects.none(), Ownership.objects.none())
    
    # Operator / Admin melihat semua data (atau bisa difilter jika perlu)

    # --- 2. FILTER BERDASARKAN QUERY PARAMS (Asset, Project, Period) ---

    # A. Filter Aset
    if asset_id and asset_id != 'all':
        try:
            asset_id_int = int(asset_id)
            
            # Security Check untuk Investor: Jangan izinkan intip aset orang lain
            if user.role and user.role.name == 'Investor':
                if not Ownership.objects.filter(investor__user=user, asset_id=asset_id_int).exists():
                     return (Funding.objects.none(), Expense.objects.none(), 
                            Production.objects.none(), Ownership.objects.none())

            # [FIX] Konsisten menggunakan project_id untuk Expense
            expenses_qs = expenses_qs.filter(project_id__asset_id=asset_id_int)
            
            productions_qs = productions_qs.filter(asset_id=asset_id_int)
            ownerships_qs = ownerships_qs.filter(asset_id=asset_id_int)
            fundings_qs = fundings_qs.filter(project__asset_id=asset_id_int)

        except (ValueError, TypeError):
            pass 

    # B. Filter Proyek
    if project_id and project_id != 'all':
        try:
            p_id = int(project_id)
            # [FIX] Expense menggunakan project_id
            expenses_qs = expenses_qs.filter(project_id=p_id)
            fundings_qs = fundings_qs.filter(project_id=p_id)
        except (ValueError, TypeError):
            pass

    # C. Filter Periode (Date Handling)
    if period and period != 'all':
        try:
            year, month, quarter = None, None, None
            date_filters = {}
            funding_date_filters = {}

            if 'Q' in period: # Format YYYY-Qn
                parts = period.split('-')
                if len(parts) == 2:
                    year = int(parts[0])
                    quarter = int(parts[1].replace('Q', ''))
                    month_start = (quarter - 1) * 3 + 1
                    month_end = quarter * 3
                    
                    date_filters = {'date__year': year, 'date__month__gte': month_start, 'date__month__lte': month_end}
                    funding_date_filters = {'date_received__year': year, 'date_received__month__gte': month_start, 'date_received__month__lte': month_end}

            elif '-' in period: # Format YYYY-MM
                parts = period.split('-')
                if len(parts) == 2:
                    year = int(parts[0])
                    month = int(parts[1])
                    date_filters = {'date__year': year, 'date__month': month}
                    funding_date_filters = {'date_received__year': year, 'date_received__month': month}
                
            else: # Format YYYY
                year = int(period)
                date_filters = {'date__year': year}
                funding_date_filters = {'date_received__year': year}

            if date_filters:
                fundings_qs = fundings_qs.filter(**funding_date_filters)
                expenses_qs = expenses_qs.filter(**date_filters)
                productions_qs = productions_qs.filter(**date_filters)

        except (ValueError, TypeError, IndexError):
            pass 

    return fundings_qs, expenses_qs, productions_qs, ownerships_qs


# =================================================================================
# ENDPOINT VIEWS
# =================================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def laporan_keuangan(request):
    fundings_qs, expenses_qs, productions_qs, _ = get_filtered_querysets(request)

    total_dana = fundings_qs.aggregate(
        total=Coalesce(Sum('amount'), Decimal(0), output_field=DecimalField())
    )['total']
    
    total_pengeluaran = expenses_qs.aggregate(
        total=Coalesce(Sum('amount'), Decimal(0), output_field=DecimalField())
    )['total']
    
    total_yield = productions_qs.aggregate(
        total_value=Coalesce(Sum(F('quantity') * F('unit_price')), Decimal(0), output_field=DecimalField())
    )['total_value'] 

    laba_rugi = total_yield - total_pengeluaran
    sisa_dana = total_dana - total_pengeluaran 

    status_keuangan = "Impas"
    if laba_rugi > 0: status_keuangan = "Laba"
    elif laba_rugi < 0: status_keuangan = "Rugi"

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
    _, expenses_qs, _, _ = get_filtered_querysets(request)
    
    category_data = expenses_qs.values('category').annotate(
        total=Coalesce(Sum('amount'), Decimal(0), output_field=DecimalField())
    ).order_by('-total')
    
    result = [
        {"category": item['category'] or 'Lainnya', "total": float(item['total'])}
        for item in category_data if item['total'] > 0
    ]
    return Response(result, status=http_status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_pengeluaran(request):
    _, expenses_qs, _, _ = get_filtered_querysets(request)
    
    # [FIX] Gunakan project_id sesuai model Expense
    top_expenses = expenses_qs.select_related('project_id__asset', 'project_id').order_by('-amount')[:5]
    
    result = []
    for exp in top_expenses:
        # Handle potensi relation null
        # Perhatikan penggunaan .project_id (object relation)
        asset_name = "-"
        project_name = "-"
        
        if exp.project_id:
            project_name = exp.project_id.name
            if exp.project_id.asset:
                asset_name = exp.project_id.asset.name

        result.append({
            "id": exp.id,
            "amount": float(exp.amount),
            "description": exp.description,
            "asset": asset_name,
            "project": project_name,
            "date": exp.date.isoformat(),
            "category": exp.category,
            "proof_url": exp.proof_url 
        })
        
    return Response(result, status=http_status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pendapatan_vs_pengeluaran(request):
    _, expenses_qs, productions_qs, _ = get_filtered_querysets(request)
    
    monthly_income_data = productions_qs.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total_income=Coalesce(Sum(F('quantity') * F('unit_price')), Decimal(0), output_field=DecimalField())
    ).order_by('month')
    
    monthly_expense_data = expenses_qs.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total_expense=Coalesce(Sum('amount'), Decimal(0), output_field=DecimalField())
    ).order_by('month')

    data_map = defaultdict(lambda: {"income": 0, "expense": 0})
    
    for item in monthly_income_data:
        if item['month']:
            month_key = item['month'].strftime('%Y-%m')
            data_map[month_key]["income"] = float(item['total_income'])
        
    for item in monthly_expense_data:
        if item['month']:
            month_key = item['month'].strftime('%Y-%m')
            data_map[month_key]["expense"] = float(item['total_expense'])
        
    sorted_months = sorted(data_map.keys())
    
    result = [
        {
            "month": month,
            "income": data_map[month]["income"],
            "expense": data_map[month]["expense"]
        }
        for month in sorted_months
    ]

    return Response(result, status=http_status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ringkasan_kuartal(request):
    fundings_qs, expenses_qs, productions_qs, _ = get_filtered_querysets(request)

    def aggregate_by_quarter(queryset, date_field, sum_field):
        return queryset.annotate(
            year=ExtractYear(date_field),
            quarter=ExtractQuarter(date_field)
        ).values('year', 'quarter').annotate(
            total=Coalesce(Sum(sum_field), Decimal(0), output_field=DecimalField())
        ).order_by('year', 'quarter')

    funding_q = aggregate_by_quarter(fundings_qs, 'date_received', 'amount')
    expense_q = aggregate_by_quarter(expenses_qs, 'date', 'amount')
    yield_q = aggregate_by_quarter(productions_qs, 'date', F('quantity') * F('unit_price'))

    data_map = defaultdict(lambda: {"funding": 0, "expense": 0, "yield": 0})
    
    for item in funding_q:
        key = f"{item['year']}-Q{item['quarter']}"
        data_map[key]["funding"] = float(item['total'])
        
    for item in expense_q:
        key = f"{item['year']}-Q{item['quarter']}"
        data_map[key]["expense"] = float(item['total'])
        
    for item in yield_q:
        key = f"{item['year']}-Q{item['quarter']}"
        data_map[key]["yield"] = float(item['total'])
        
    sorted_quarters = sorted(data_map.keys())

    result = []
    for q in sorted_quarters:
        data = data_map[q]
        net_profit = data["yield"] - data["expense"]
        result.append({
            "quarter": q,
            "funding": data["funding"],
            "expense": data["expense"],
            "yield": data["yield"],
            "net_profit": net_profit
        })
    
    return Response(result, status=http_status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def yield_report(request):
    fundings_qs, expenses_qs, productions_qs, _ = get_filtered_querysets(request)
    
    total_investasi = fundings_qs.aggregate(
        total=Coalesce(Sum('amount'), Decimal(0), output_field=DecimalField())
    )['total']
    
    total_yield = productions_qs.aggregate(
        total=Coalesce(Sum(F('quantity') * F('unit_price')), Decimal(0), output_field=DecimalField())
    )['total']
    
    total_expense = expenses_qs.aggregate(
        total=Coalesce(Sum('amount'), Decimal(0), output_field=DecimalField())
    )['total']
    
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
    fundings_qs, _, productions_qs, ownerships_qs = get_filtered_querysets(request)
    
    asset_yields = productions_qs.values('asset').annotate(
        total_yield=Coalesce(Sum(F('quantity') * F('unit_price')), Decimal(0), output_field=DecimalField())
    )
    asset_yield_map = {item['asset']: item['total_yield'] for item in asset_yields}
    
    funding_map = {item['id']: item['amount'] for item in fundings_qs.values('id', 'amount')}

    investor_data = defaultdict(lambda: {"total_funding": Decimal(0), "total_yield": Decimal(0)})
    
    for own in ownerships_qs.select_related('investor__user', 'funding', 'asset'):
        investor_name = own.investor.user.username
        percentage = Decimal(own.ownership_percentage) / 100 if own.ownership_percentage else Decimal(0)
        
        funding_amount = funding_map.get(own.funding_id, Decimal(0))
        investor_data[investor_name]["total_funding"] += (funding_amount * percentage)
        
        asset_yield = asset_yield_map.get(own.asset_id, Decimal(0))
        investor_data[investor_name]["total_yield"] += (asset_yield * percentage)

    result = []
    for name, data in investor_data.items():
        total_funding_float = float(data["total_funding"])
        total_yield_float = float(data["total_yield"])
        yield_percent = (total_yield_float / total_funding_float * 100) if total_funding_float > 0 else 0
        result.append({
            "investor": name,
            "total_funding": total_funding_float,
            "total_yield": total_yield_float,
            "yield_percent": round(yield_percent, 1)
        })
    
    return Response(result, status=http_status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def funding_progress(request):
    fundings_qs, expenses_qs, _, _ = get_filtered_querysets(request)

    total_funding = fundings_qs.aggregate(
        total=Coalesce(Sum('amount'), Decimal(0), output_field=DecimalField())
    )['total']
    
    total_expense = expenses_qs.aggregate(
        total=Coalesce(Sum('amount'), Decimal(0), output_field=DecimalField())
    )['total']
    
    total = total_funding + total_expense
    funding_percent = (float(total_funding) / float(total) * 100) if total > 0 else 0
    expense_percent = (float(total_expense) / float(total) * 100) if total > 0 else 0
    
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
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rincian_dana_per_proyek(request):
    user = request.user
    project_id = request.GET.get('project')
    
    projects_qs = Project.objects.select_related('asset').all()
    
    # 1. Filter Proyek untuk Investor
    if user.role and user.role.name == 'Investor':
        try:
            investor = user.investor
            owned_asset_ids = Ownership.objects.filter(investor=investor).values_list('asset_id', flat=True).distinct()
            projects_qs = projects_qs.filter(asset_id__in=owned_asset_ids)
        except Investor.DoesNotExist:
            projects_qs = Project.objects.none()
    
    # 2. Filter by ID Param
    if project_id and project_id != 'all':
        try:
            projects_qs = projects_qs.filter(id=int(project_id))
        except (ValueError, TypeError):
            pass
    
    result = []
    for project in projects_qs: 
        anggaran = float(project.budget)
        
        total_dana_masuk = Funding.objects.filter(
            project_id=project.id
        ).aggregate(
            total=Coalesce(Sum('amount'), Decimal(0), output_field=DecimalField())
        )['total']
        
        # [FIX] Expense query
        total_pengeluaran = Expense.objects.filter(
            project_id=project.id
        ).aggregate(
            total=Coalesce(Sum('amount'), Decimal(0), output_field=DecimalField())
        )['total']
        
        sisa_dana = float(total_dana_masuk) - float(total_pengeluaran)
        
        persen_dana_masuk = (float(total_dana_masuk) / anggaran * 100) if anggaran > 0 else 0
        persen_sisa_anggaran = 100 - persen_dana_masuk
        
        persen_pengeluaran = (float(total_pengeluaran) / float(total_dana_masuk) * 100) if total_dana_masuk > 0 else 0
        persen_sisa_dana = 100 - persen_pengeluaran
        
        result.append({
            "project_id": project.id,
            "project_name": project.name,
            "anggaran": anggaran,
            "total_dana_masuk": float(total_dana_masuk),
            "total_pengeluaran": float(total_pengeluaran),
            "sisa_dana": sisa_dana,
            "progress_funding": {
                "dana_masuk_percent": round(persen_dana_masuk, 1),
                "sisa_anggaran_percent": round(persen_sisa_anggaran, 1)
            },
            "progress_expense": {
                "pengeluaran_percent": round(persen_pengeluaran, 1),
                "sisa_dana_percent": round(persen_sisa_dana, 1)
            }
        })
    
    return Response(result, status=http_status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def production_statistics(request):
    """
    Menghitung 4 statistik untuk kartu di halaman Produksi (Total, Nilai, Terjual, Stok).
    """
    # Reuse helper agar logic filternya sama (Aman untuk Investor)
    _, _, productions_qs, _ = get_filtered_querysets(request)

    # 1. Total Produksi (Count)
    total_produksi = productions_qs.count()
    
    # 2. Nilai Total (Sum dari total_value)
    nilai_total = productions_qs.aggregate(
        total=Coalesce(Sum('total_value'), Decimal(0), output_field=DecimalField())
    )['total']
    
    # 3. Terjual
    terjual = productions_qs.filter(status='terjual').aggregate(
        total=Coalesce(Sum('total_value'), Decimal(0), output_field=DecimalField())
    )['total']
        
    # 4. Stok
    stok = productions_qs.filter(status='stok').aggregate(
        total=Coalesce(Sum('total_value'), Decimal(0), output_field=DecimalField())
    )['total']

    data = {
        "total_produksi": total_produksi,
        "nilai_total": float(nilai_total),
        "terjual": float(terjual),
        "stok": float(stok)
    }
    
    return Response(data, status=http_status.HTTP_200_OK)