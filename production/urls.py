from django.urls import path
from . import views

urlpatterns = [
    path('productions/', views.production_list, name='production-list'),
    path('productions/<int:pk>/', views.production_detail, name='production-detail'),
]
