from django.urls import path
from . import views

urlpatterns = [
    path('investors/', views.investor_list_create, name='investor-list-create'),
    path('investors/<int:pk>/', views.investor_detail, name='investor-detail'),
]
