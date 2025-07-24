from django.urls import path
from .import views

urlpatterns = [
    path('expense/', views.list_expanse),
    path('expense/tambah/', views.tambah_expanse),
]
