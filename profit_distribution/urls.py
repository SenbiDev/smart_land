from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_distribution, name='list-distribution'),
    path('create/', views.create_distribution, name='create-distribution'),
    path('<int:pk>/', views.distribution_detail, name='detail-distribution'),
]