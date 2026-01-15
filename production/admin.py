from django.contrib import admin
from .models import Production, Product

# 1. Daftarkan Master Product (Agar bisa buat Stok Awal: Padi, Jagung, dll)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_stock', 'unit')
    search_fields = ('name',)

# 2. Perbaiki Production Admin
@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    # [UBAH] Ganti 'product_name' & 'unit' jadi 'product'
    list_display = ('product', 'asset', 'quantity', 'quality', 'date')
    list_filter = ('quality', 'date', 'asset')
    search_fields = ('product__name', 'asset__name') # Cari berdasarkan nama produk/aset