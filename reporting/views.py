from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, F, DecimalField, Q, Count
from django.db.models.functions import Coalesce, TruncMonth, ExtractQuarter, ExtractYear
from decimal import Decimal
import datetime
from collections import defaultdict # Untuk merge data

# Import semua model yang diperlukan
from funding.models import Funding
from expense.models import Expense
from production.models import Production
from ownership.models import Ownership 
from investor.models import Investor
from project.models import Project
# (Asumsi Anda juga memiliki model Project, jika tidak, hapus filter 'project_id')
# from project.models import Project 

# --- FUNGSI HELPER UTAMA UNTUK FILTER ---

def get_filtered_querysets(request):
    """
    Satu fungsi untuk mendapatkan semua queryset dasar, 
    sudah difilter berdasarkan role user DAN query params.
    """
    user = request.user
    
    # Ambil query params
    asset_id = request.GET.get('asset')
    project_id = request.GET.get('project')
    period = request.GET.get('period') # Format 'YYYY-MM', 'YYYY-Qn', atau 'YYYY'

    # Queryset dasar
    fundings_qs = Funding.objects.all()
    expenses_qs = Expense.objects.all()
    productions_qs = Production.objects.all()
    ownerships_qs = Ownership.objects.all()

    # --- 1. Filter berdasarkan Role Investor ---
    if user.role == 'Investor':
        try:
            investor = user.investor
            investor_ownerships = Ownership.objects.filter(investor=investor)
            asset_ids = investor_ownerships.values_list('asset_id', flat=True).distinct()
            funding_ids = investor_ownerships.values_list('funding_id', flat=True).distinct()
            
            # Filter queryset dasar HANYA untuk data investor
            fundings_qs = fundings_qs.filter(id__in=funding_ids)
            expenses_qs = expenses_qs.filter(
                Q(asset_id__in=asset_ids) | Q(funding_id__in=funding_ids)
            ).distinct()
            productions_qs = productions_qs.filter(asset_id__in=asset_ids)
            ownerships_qs = ownerships_qs.filter(investor=investor)
            
        except Investor.DoesNotExist:
            # Jika profil investor tidak ada, return queryset kosong
            return (Funding.objects.none(), Expense.objects.none(), 
                    Production.objects.none(), Ownership.objects.none())

    # --- 2. Filter berdasarkan Query Params (Aset, Proyek, Periode) ---

    # Filter Aset
    if asset_id and asset_id != 'all':
        try:
            asset_id_int = int(asset_id)
            expenses_qs = expenses_qs.filter(asset_id=asset_id_int)
            productions_qs = productions_qs.filter(asset_id=asset_id_int)
            ownerships_qs = ownerships_qs.filter(asset_id=asset_id_int)
            # Funding terkait ownership, jadi filter funding berdasarkan ownerships
            funding_ids_from_asset = Ownership.objects.filter(asset_id=asset_id_int).values_list('funding_id', flat=True)
            fundings_qs = fundings_qs.filter(id__in=funding_ids_from_asset)
        except (ValueError, TypeError):
            pass # Abaikan jika asset_id tidak valid

    # Filter Proyek
    if project_id and project_id != 'all':
        try:
            project_id_int = int(project_id)
            # Proyek biasanya terkait dengan Pengeluaran
            expenses_qs = expenses_qs.filter(project_id=project_id_int)
            # (Jika model Production juga punya FK ke Project, tambahkan di sini)
            # productions_qs = productions_qs.filter(project_id=project_id_int) 
        except (ValueError, TypeError):
            pass

    # Filter Periode
    if period and period != 'all':
        try:
            year, month, quarter = None, None, None
            date_filters = {}
            funding_date_filters = {}

            if 'Q' in period: # Format YYYY-Qn
                year_str, quarter_str = period.split('-')
                year = int(year_str)
                quarter = int(quarter_str[1])
                month_start = (quarter - 1) * 3 + 1
                month_end = quarter * 3
                
                date_filters = {'date__year': year, 'date__month__gte': month_start, 'date__month__lte': month_end}
                funding_date_filters = {'date_received__year': year, 'date_received__month__gte': month_start, 'date_received__month__lte': month_end}

            elif '-' in period: # Format YYYY-MM
                year_str, month_str = period.split('-')
                year = int(year_str)
                month = int(month_str)
                
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
            pass # Abaikan jika format periode tidak valid

    return fundings_qs, expenses_qs, productions_qs, ownerships_qs


# --- ENDPOINT VIEWS (Sudah direfactor) ---

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def laporan_keuangan(request):
    # Cukup panggil helper
    fundings_qs, expenses_qs, productions_qs, _ = get_filtered_querysets(request)

    # Gunakan Coalesce untuk menghindari None saat Sum() kosong
    total_dana = fundings_qs.aggregate(
        total=Coalesce(Sum('amount'), Decimal(0), output_field=DecimalField())
    )['total']
    
    total_pengeluaran = expenses_qs.aggregate(
        total=Coalesce(Sum('amount'), Decimal(0), output_field=DecimalField())
    )['total']
    
    total_yield = productions_qs.aggregate(
        total_value=Coalesce(Sum(F('quantity') * F('unit_price')), Decimal(0), output_field=DecimalField())
    )['total_value'] # Ganti nama key 'total'

    laba_rugi = total_yield - total_pengeluaran
    sisa_dana = total_dana - total_pengeluaran # (Asumsi sisa dana = total funding - total expense)

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
    # Cukup panggil helper
    _, expenses_qs, _, _ = get_filtered_querysets(request)
    
    category_data = expenses_qs.values('category').annotate(
        total=Coalesce(Sum('amount'), Decimal(0), output_field=DecimalField())
    ).order_by('-total')
    
    # Sesuaikan key di result agar konsisten
    result = [
        {"category": item['category'] or 'Lainnya', "total": float(item['total'])}
        for item in category_data if item['total'] > 0
    ]
    return Response(result, status=http_status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_pengeluaran(request):
    # Cukup panggil helper
    _, expenses_qs, _, _ = get_filtered_querysets(request)
    
    # Gunakan .values() untuk data yang lebih bersih
    top_expenses = expenses_qs.order_by('-amount').values(
        'id', 'amount', 'description', 'date', 'category', 
        'asset_id__name', 'project_id__name' # Ambil nama relasi
    )[:5]
    
    result = [
        {
            "id": exp['id'],
            "amount": float(exp['amount']),
            "description": exp['description'],
            "asset": exp['asset_id__name'], # Nama aset
            "project": exp['project_id__name'], # Nama proyek
            "date": exp['date'].isoformat(),
            "category": exp['category']
        }
        for exp in top_expenses
    ]
    return Response(result, status=http_status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pendapatan_vs_pengeluaran(request):
    # Cukup panggil helper
    _, expenses_qs, productions_qs, _ = get_filtered_querysets(request)
    
    # Group production by month menggunakan DB
    monthly_income_data = productions_qs.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total_income=Coalesce(Sum(F('quantity') * F('unit_price')), Decimal(0), output_field=DecimalField())
    ).order_by('month')
    
    # Group expenses by month menggunakan DB
    monthly_expense_data = expenses_qs.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total_expense=Coalesce(Sum('amount'), Decimal(0), output_field=DecimalField())
    ).order_by('month')

    # Gabungkan data di Python
    data_map = defaultdict(lambda: {"income": 0, "expense": 0})
    
    for item in monthly_income_data:
        month_key = item['month'].strftime('%Y-%m')
        data_map[month_key]["income"] = float(item['total_income'])
        
    for item in monthly_expense_data:
        month_key = item['month'].strftime('%Y-%m')
        data_map[month_key]["expense"] = float(item['total_expense'])
        
    # Urutkan berdasarkan key (bulan)
    sorted_months = sorted(data_map.keys())
    
    result = [
        {
            "month": month,
            "income": data_map[month]["income"],
            "expense": data_map[month]["expense"]
        }
        for month in sorted_months
    ]

    # Hapus slice '[-6:]' agar filter periode berfungsi
    return Response(result, status=http_status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ringkasan_kuartal(request):
    # Cukup panggil helper
    fundings_qs, expenses_qs, productions_qs, _ = get_filtered_querysets(request)

    # Helper untuk agregasi per kuartal
    def aggregate_by_quarter(queryset, date_field, sum_field):
        return queryset.annotate(
            year=ExtractYear(date_field),
            quarter=ExtractQuarter(date_field)
        ).values('year', 'quarter').annotate(
            total=Coalesce(Sum(sum_field), Decimal(0), output_field=DecimalField())
        ).order_by('year', 'quarter')

    # Agregasi data
    funding_q = aggregate_by_quarter(fundings_qs, 'date_received', 'amount')
    expense_q = aggregate_by_quarter(expenses_qs, 'date', 'amount')
    yield_q = aggregate_by_quarter(productions_qs, 'date', F('quantity') * F('unit_price'))

    # Gabungkan data
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
        
    # Urutkan berdasarkan key (kuartal)
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
    # Cukup panggil helper
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
    # Panggil helper
    fundings_qs, _, productions_qs, ownerships_qs = get_filtered_querysets(request)
    
    # 1. Hitung total yield per aset (dari produksi yang sudah difilter)
    asset_yields = productions_qs.values('asset').annotate(
        total_yield=Coalesce(Sum(F('quantity') * F('unit_price')), Decimal(0), output_field=DecimalField())
    )
    asset_yield_map = {item['asset']: item['total_yield'] for item in asset_yields}
    
    # 2. Ambil data funding (dari funding yang sudah difilter)
    funding_map = {item['id']: item['amount'] for item in fundings_qs.values('id', 'amount')}

    # 3. Proses ownership (dari ownerships yang sudah difilter)
    investor_data = defaultdict(lambda: {"total_funding": Decimal(0), "total_yield": Decimal(0)})
    
    # Gunakan select_related untuk efisiensi
    for own in ownerships_qs.select_related('investor__user', 'funding', 'asset'):
        investor_name = own.investor.user.username
        percentage = Decimal(own.ownership_percentage) / 100
        
        # Akumulasi funding berdasarkan persentase kepemilikan
        funding_amount = funding_map.get(own.funding_id, Decimal(0))
        investor_data[investor_name]["total_funding"] += (funding_amount * percentage)
        
        # Akumulasi yield berdasarkan persentase kepemilikan
        asset_yield = asset_yield_map.get(own.asset_id, Decimal(0))
        investor_data[investor_name]["total_yield"] += (asset_yield * percentage)

    # Format hasil
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
    # Cukup panggil helper
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
    
# ==================== ENDPOINT BARU: RINCIAN DANA PER PROYEK ====================
# Sesuai dengan UI gambar: Anggaran, Total Dana Masuk, Pengeluaran, Sisa, %

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rincian_dana_per_proyek(request):
    """
    Menampilkan rincian dana berdasarkan proyek:
    - Anggaran (Project.budget)
    - Total Dana Masuk (dari Ownership -> Funding yang terkait aset proyek)
    - Pengeluaran (dari Expense yang terkait proyek)
    - Sisa Dana
    - Persentase Progress (Dana Masuk/Anggaran, Pengeluaran/Dana Masuk)
    """
    user = request.user
    project_id = request.GET.get('project')
    
    # Base queryset proyek
    projects_qs = Project.objects.all()
    
    # --- Filter khusus Investor ---
    if user.role == 'Investor':
        try:
            investor = user.investor
            owned_asset_ids = Ownership.objects.filter(investor=investor).values_list('asset_id', flat=True).distinct()
            
            # Proyek yang terkait dengan aset yang dimiliki investor (via Expense)
            relevant_project_ids = Expense.objects.filter(
                asset_id__in=owned_asset_ids,
                project_id__isnull=False
            ).values_list('project_id', flat=True).distinct()
            
            projects_qs = projects_qs.filter(id__in=relevant_project_ids)
        except Investor.DoesNotExist:
            projects_qs = Project.objects.none()
    
    # --- Filter project_id jika ada ---
    if project_id and project_id != 'all':
        try:
            projects_qs = projects_qs.filter(id=int(project_id))
        except (ValueError, TypeError):
            pass
    
    # --- Proses setiap proyek ---
    result = []
    for project in projects_qs:
        # 1. Anggaran
        anggaran = float(project.budget)
        
        # 2. Total Dana Masuk
        # Logika: Ambil asset_id dari Expense yang terkait proyek ini
        # Lalu sum funding dari Ownership yang berinvestasi di aset tersebut
        asset_ids = Expense.objects.filter(project_id=project.id).values_list('asset_id', flat=True).distinct()
        
        total_dana_masuk = Ownership.objects.filter(
            asset_id__in=asset_ids
        ).aggregate(
            total=Coalesce(Sum('funding__amount'), Decimal(0), output_field=DecimalField())
        )['total']
        
        # 3. Total Pengeluaran
        total_pengeluaran = Expense.objects.filter(
            project_id=project.id
        ).aggregate(
            total=Coalesce(Sum('amount'), Decimal(0), output_field=DecimalField())
        )['total']
        
        # 4. Sisa Dana
        sisa_dana = float(total_dana_masuk) - float(total_pengeluaran)
        
        # 5. Persentase
        # Progress Bar 1: Dana Masuk/Anggaran (hijau vs abu)
        persen_dana_masuk = (float(total_dana_masuk) / anggaran * 100) if anggaran > 0 else 0
        persen_sisa_anggaran = 100 - persen_dana_masuk
        
        # Progress Bar 2: Pengeluaran/Dana Masuk (biru vs ungu)
        persen_pengeluaran = (float(total_pengeluaran) / float(total_dana_masuk) * 100) if total_dana_masuk > 0 else 0
        persen_sisa_dana = 100 - persen_pengeluaran
        
        result.append({
            "project_id": project.id,
            "project_name": project.name,
            "anggaran": anggaran,
            "total_dana_masuk": float(total_dana_masuk),
            "total_pengeluaran": float(total_pengeluaran),
            "sisa_dana": sisa_dana,
            
            # Progress Bar 1 (Dana Masuk vs Anggaran)
            "progress_funding": {
                "dana_masuk_percent": round(persen_dana_masuk, 1),
                "sisa_anggaran_percent": round(persen_sisa_anggaran, 1)
            },
            
            # Progress Bar 2 (Pengeluaran vs Sisa Dana)
            "progress_expense": {
                "pengeluaran_percent": round(persen_pengeluaran, 1),
                "sisa_dana_percent": round(persen_sisa_dana, 1)
            }
        })
    
    return Response(result, status=http_status.HTTP_200_OK)