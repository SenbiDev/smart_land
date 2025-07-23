from django.urls import path
from . import views  

urlpatterns = [
    path('Aset/', views.list_aset),
    path('aset/tambah', views.tambah_aset),
    path('asset/<int:pk>/', views.asset_detail),
    path('owner/', views.list_owner),
    path('owner/tambah', views.tambah_owner),
    path('owner/<int:pk>/', views.owner_detail),
]
