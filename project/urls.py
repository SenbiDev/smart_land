from django.urls import path
from . import views 

urlpatterns = [
    path('projects/', views.list_project),
    path('projectss/tambah/', views.tambah_project),
    path('projectsss/<int:pk>', views.project_detail)
]
