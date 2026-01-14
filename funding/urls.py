from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_funding, name='list-funding'),
    path('create/', views.create_funding, name='create-funding'),
    path('<int:pk>/', views.funding_detail, name='detail-funding'),
]