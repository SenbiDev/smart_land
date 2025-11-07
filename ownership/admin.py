from django.contrib import admin
from .models import Ownership

@admin.register(Ownership)
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'investor', 'asset', 'funding', 'units', 'ownership_percentage', 'investment_date')
    list_filter = ('investment_date', 'funding')
    search_fields = ('investor__user__username', 'asset__name')