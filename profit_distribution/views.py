from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import Sum
from decimal import Decimal, InvalidOperation
from datetime import datetime
from .models import ProfitDistribution, ProfitDistributionItem
from .serializers import ProfitDistributionSerializer
from asset.models import Asset
from funding.models import Funding
from dashboard.models import SystemConfig
from authentication.permissions import IsOperatorOrAdmin, IsViewerOrInvestorReadOnly

# ==========================================
# 1. LIST & CREATE (GET, POST)
# ==========================================
@api_view(['GET', 'POST'])
@permission_classes([IsOperatorOrAdmin | IsViewerOrInvestorReadOnly])
def list_create_distributions(request):
    if request.method == 'GET':
        queryset = ProfitDistribution.objects.prefetch_related('items').all().order_by('-date')
        serializer = ProfitDistributionSerializer(queryset, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Cek permission manual
        user_role = getattr(request.user.role, 'name', '') if request.user.role else ''
        if user_role not in ['Admin', 'Superadmin', 'Operator']:
             return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        
        # Validasi dan konversi nominal dengan Decimal
        raw_amount = data.get('total_distributed') or data.get('total_amount') or 0
        try:
            total_amount = Decimal(str(raw_amount))
        except (InvalidOperation, ValueError, TypeError):
            return Response(
                {"detail": f"Nominal tidak valid: {raw_amount}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if total_amount <= 0:
            return Response(
                {"detail": "Nominal harus lebih dari 0"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validasi dan parsing tanggal
        date_str = data.get('date')
        if not date_str:
            return Response(
                {"detail": "Tanggal harus diisi"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            distribution_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return Response(
                {"detail": f"Format tanggal tidak valid: {date_str}. Gunakan YYYY-MM-DD"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # 1. Simpan Header
                distribution = ProfitDistribution.objects.create(
                    total_distributed=total_amount,
                    notes=data.get('notes', 'Bagi Hasil'),
                    date=distribution_date
                )

                # 2. Ambil Dana Investor Aktif
                # ⚠️ FIX: Hapus .select_related('user') karena tidak ada field user
                investor_fundings = Funding.objects.filter(source_type='investor')
                
                items = []
                
                # A. Potongan Landowner
                active_assets = Asset.objects.all()
                total_landowner_cut = Decimal('0')
                
                for asset in active_assets:
                    try:
                        pct = Decimal(str(asset.landowner_share_percentage or 0))
                    except (InvalidOperation, ValueError, TypeError):
                        pct = Decimal('0')
                    
                    if pct > 0:
                        cut = (total_amount * pct) / Decimal('100')
                        total_landowner_cut += cut
                        
                        items.append(ProfitDistributionItem(
                            distribution=distribution,
                            amount=cut,
                            role='Landowner',
                            description=f"Fee Lahan: {asset.name}"
                        ))

                # B. Bagian Investor
                net_for_investors = total_amount - total_landowner_cut
                
                # Ambil Config Saham
                try:
                    config = SystemConfig.objects.first()
                    TOTAL_SYSTEM_SHARES = Decimal(str(config.total_system_shares if config else 15000))
                except:
                    TOTAL_SYSTEM_SHARES = Decimal('15000')

                # Hitung Dividen Per Lembar
                dividend_per_share = Decimal('0')
                if TOTAL_SYSTEM_SHARES > 0:
                    dividend_per_share = net_for_investors / TOTAL_SYSTEM_SHARES

                # Bagikan ke Investor
                for funding in investor_fundings:
                    try:
                        shares = Decimal(str(getattr(funding, 'shares', 0) or 0))
                    except (InvalidOperation, ValueError, TypeError, AttributeError):
                        shares = Decimal('0')
                    
                    if shares > 0:
                        investor_share = shares * dividend_per_share
                        
                        # ⚠️ FIX: Jangan assign investor=funding.user karena tidak ada
                        items.append(ProfitDistributionItem(
                            distribution=distribution,
                            investor=None,  # Set None karena Funding tidak punya relasi User
                            funding_source=funding,
                            amount=investor_share,
                            role='Investor',
                            description=f"{funding.source_name} - Dividen ({shares:,.0f} lbr)"
                        ))
                
                # Simpan Items
                if items:
                    ProfitDistributionItem.objects.bulk_create(items)

                serializer = ProfitDistributionSerializer(distribution)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"❌ Error Distribution: {e}")
            print(f"📋 Traceback: {error_detail}")
            return Response(
                {"detail": f"Terjadi kesalahan: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ==========================================
# 2. PREVIEW (POST)
# ==========================================
@api_view(['POST'])
@permission_classes([IsOperatorOrAdmin])
def preview_distribution(request):
    try:
        raw_amount = request.data.get('total_distributed') or request.data.get('total_amount') or 0
        
        try:
            total_amount = Decimal(str(raw_amount))
        except (InvalidOperation, ValueError, TypeError):
            return Response(
                {"detail": "Nominal tidak valid"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if total_amount <= 0:
            return Response(
                {"detail": "Nominal harus lebih dari 0"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Hitung Potongan Landowner
        active_assets = Asset.objects.all()
        total_landowner_cut = Decimal('0')
        
        for asset in active_assets:
            try:
                pct = Decimal(str(asset.landowner_share_percentage or 0))
            except (InvalidOperation, ValueError, TypeError):
                pct = Decimal('0')
            
            if pct > 0:
                total_landowner_cut += (total_amount * pct) / Decimal('100')

        # 2. Dana Bersih untuk Investor
        net_for_investors = total_amount - total_landowner_cut
        
        # 3. Ambil Config & Hitung Dividen
        try:
            config = SystemConfig.objects.first()
            TOTAL_SYSTEM_SHARES = Decimal(str(config.total_system_shares if config else 15000))
        except:
            TOTAL_SYSTEM_SHARES = Decimal('15000')
        
        dividend_per_share = net_for_investors / TOTAL_SYSTEM_SHARES if TOTAL_SYSTEM_SHARES > 0 else Decimal('0')

        # 4. Data Investor Saham
        investor_fundings = Funding.objects.filter(source_type='investor')
        investor_rows = []
        total_payout_to_investors = Decimal('0')

        for f in investor_fundings:
            try:
                shares = Decimal(str(getattr(f, 'shares', 0) or 0))
            except (InvalidOperation, ValueError, TypeError, AttributeError):
                shares = Decimal('0')
            
            if shares > 0:
                payout = shares * dividend_per_share
                total_payout_to_investors += payout
                investor_rows.append({
                    "name": f.source_name,  # ✅ Gunakan source_name dari Funding
                    "role": "Investor",
                    "portion_info": f"{shares:,.0f} Lbr",
                    "amount": float(payout)
                })

        return Response({
            "summary": {
                "total_input": float(total_amount),
                "landowner_total": float(total_landowner_cut),
                "investor_net_pool": float(net_for_investors),
                "dividend_per_share": float(dividend_per_share),
                "retained_earnings": float(net_for_investors - total_payout_to_investors),
            },
            "investor_breakdown": investor_rows
        })
        
    except Exception as e:
        import traceback
        print(f"❌ Preview Error: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")
        return Response(
            {"detail": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

# ==========================================
# 3. DETAIL & DELETE
# ==========================================
@api_view(['GET', 'DELETE'])
@permission_classes([IsOperatorOrAdmin | IsViewerOrInvestorReadOnly])
def distribution_detail(request, pk):
    try:
        dist = ProfitDistribution.objects.prefetch_related('items').get(pk=pk)
    except ProfitDistribution.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProfitDistributionSerializer(dist)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        user_role = getattr(request.user.role, 'name', '') if request.user.role else ''
        if user_role not in ['Admin', 'Superadmin']:
             return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        dist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)