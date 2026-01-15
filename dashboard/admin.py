from django.contrib import admin
from .models import SystemConfig

@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    # --- HAPUS BARIS DI BAWAH INI (INI PENYEBAB ERRORNYA) ---
    # fields = ('total_system_shares', 'share_price') 
    
    # Field Read-Only (Laporan)
    readonly_fields = ('total_cash_on_hand', 'total_asset_value', 'shares_sold', 'shares_available')

    # Gunakan Fieldsets saja (Lebih rapi)
    fieldsets = (
        ('Konfigurasi Global', {
            'fields': ('total_system_shares', 'share_price'),
            'description': 'Atur jumlah saham dan harga dasar di sini.'
        }),
        ('Laporan Global (Real-time)', {
            'fields': (
                'total_cash_on_hand', 
                'total_asset_value', 
                'shares_sold', 
                'shares_available'
            ),
            'classes': ('wide', 'extrapretty'), 
        }),
    )

    # Mencegah Admin membuat lebih dari 1 konfigurasi
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return True