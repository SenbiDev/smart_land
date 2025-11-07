from django.urls import path
from . import views

urlpatterns = [
    path('ownerships/', views.ownership_list, name='ownership-list'),
    path('ownerships/<int:pk>/', views.ownership_detail, name='ownership-detail'),
    path('ownerships/summary/', views.ownership_summary, name='ownership-summary'),
    path('ownerships/composition/', views.ownership_composition, name='ownership-composition'),
]