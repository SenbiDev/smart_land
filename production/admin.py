from django.contrib import admin
from django.contrib import admin
from .models import Production

# Register your models here.
@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = ('asset', 'date', 'quantity', 'unit', 'unit_price', 'total_value', 'created_at')
    list_filter = ('asset', 'date')
    search_fields = ('asset__name',)