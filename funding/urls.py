from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_funding, name='list-funding'),  # Hapus 'fundings/'
    path('<int:pk>/', views.funding_detail, name='detail-funding'),
]