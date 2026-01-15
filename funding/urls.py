from django.urls import path
from . import views

urlpatterns = [
    # Ubah menjadi 'fundings/' agar URL jadi /api/funding/fundings/
    path('fundings/', views.list_funding, name='list-funding'), 
    path('fundings/create/', views.create_funding, name='create-funding'),
    path('fundings/<int:pk>/', views.funding_detail, name='detail-funding'),
]