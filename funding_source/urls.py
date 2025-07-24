from django.urls import path
from . import views

urlpatterns = [
    path('fundingsources/', views.funding_source_list, name='funding-source-list'),
    path('fundingsources/<int:pk>/', views.funding_source_detail, name='funding-source-detail'),
]