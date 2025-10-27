from django.urls import path
from .views import laporan_keuangan

urlpatterns = [
    path('laporan-keuangan/', laporan_keuangan),
]