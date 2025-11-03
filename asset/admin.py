from django.contrib import admin
from .models import Asset, Owner

# Register your models here.

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'type',
        'location',
        'size',
        'value',
        'ownership_status',
        'landowner',
        'acquisition_date',
    )
    list_filter = ('type', 'ownership_status', 'landowner')
    search_fields = ('name', 'location', 'landowner_nama')
    ordering = ('-created_at',)
    list_per_page = 20
    
@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('id', 'nama', 'kontak', 'alamat', 'bank', 'nomor_rekening')
    search_fields = ('nama', 'kontak', 'bank')
