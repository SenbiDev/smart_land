from django.contrib import admin
from .models import Production

@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = (
        'product_name', 
        'quantity', 
        'unit', 
        'quality', 
        'asset', 
        'date'
    )
    list_filter = ('quality', 'date', 'asset')
    search_fields = ('product_name', 'notes')
    ordering = ('-date',)