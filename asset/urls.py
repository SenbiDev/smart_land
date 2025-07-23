from django.urls import path
from . import views  

urlpatterns = [
    path('kategori/', views.list_kategori),
    path('kategori/tambah', views.tambah_kategori),
    path('Aset/', views.list_aset),
    path('aset/tambah', views.tambah_aset),
    path('asset/<int:pk>/', views.asset_detail),
    path('pemilik/', views.list_pemilik),
    path('pemilik/tambah', views.tambah_pemilik),
]
