from django.urls import path
from . import views 

urlpatterns = [
    path('projects/', views.list_project),
    path('projects/tambah/', views.tambah_project),
    path('projects/<int:pk>/', views.project_detail)
]