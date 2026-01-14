from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_production, name='list-production'),
    path('create/', views.create_production, name='create-production'),
    path('<int:pk>/', views.production_detail, name='detail-production'),
]