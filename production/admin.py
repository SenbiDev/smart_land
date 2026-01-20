from django.contrib import admin
from .models import Production, Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'current_stock', 'updated_at')
    search_fields = ('name',)

@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    # [FIX] Sesuaikan list_display dengan field yang ada di models.py
    # Hapus 'quality', ganti dengan 'quantity' dan 'unit_price'
    list_display = ('product', 'asset', 'date', 'quantity', 'unit_price', 'status')
    
    # [FIX] list_filter juga harus field yang valid (biasanya status dan tanggal)
    list_filter = ('status', 'date', 'asset')
    
    search_fields = ('product__name', 'asset__name')