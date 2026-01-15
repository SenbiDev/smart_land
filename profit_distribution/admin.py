from django.contrib import admin
from .models import ProfitDistribution

@admin.register(ProfitDistribution)
class ProfitDistributionAdmin(admin.ModelAdmin):
    # Kolom yang muncul di tabel list
    list_display = (
        'date', 
        'total_distributed', 
        'landowner_total_amount', 
        'investor_total_amount',
        'retained_earnings'
    )
    
    # Filter samping
    list_filter = ('date',)
    
    # Field yang hanya bisa dibaca (karena hasil hitungan otomatis)
    readonly_fields = (
        'landowner_total_amount', 
        'investor_total_amount', 
        'retained_earnings', 
        'dividend_per_share',
        'distribution_details'
    )
    
    # Urutan form input
    fields = (
        'date', 
        'total_distributed', 
        'landowner_total_amount', 
        'investor_total_amount', 
        'dividend_per_share',
        'retained_earnings',
        'distribution_details'
    )