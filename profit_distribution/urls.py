from django.urls import path
from . import views

urlpatterns = [
    # Ubah menjadi 'profit-distributions/' 
    path('profit-distributions/', views.list_distribution, name='list-distribution'),
    path('profit-distributions/create/', views.create_distribution, name='create-distribution'),
    path('profit-distributions/<int:pk>/', views.distribution_detail, name='detail-distribution'),
]