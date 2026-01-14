from django.contrib import admin
from .models import ProfitDistribution

@admin.register(ProfitDistribution)
class ProfitDistributionAdmin(admin.ModelAdmin):
    list_display = (
        'period', 
        'total_distributed', 
        'status', 
        'date'
    )
    list_filter = ('status', 'date')
    search_fields = ('period',)