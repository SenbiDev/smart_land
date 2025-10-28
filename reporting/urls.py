from django.urls import path
from . import views

urlpatterns = [
    path('laporan-keuangan/', views.laporan_keuangan, name='laporan-keuangan'),
    path('pengeluaran-per-kategori/', views.pengeluaran_per_kategori, name='pengeluaran-per-kategori'),
    path('top-pengeluaran/', views.top_pengeluaran, name='top-pengeluaran'),
    path('pendapatan-vs-pengeluaran/', views.pendapatan_vs_pengeluaran, name='pendapatan-vs-pengeluaran'),
    path('ringkasan-kuartal/', views.ringkasan_kuartal, name='ringkasan-kuartal'),
    path('yield-report/', views.yield_report, name='yield-report'),
    path('investor-yield/', views.investor_yield, name='investor-yield'),
    path('funding-progress/', views.funding_progress, name='funding-progress'),
]