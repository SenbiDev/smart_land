from django.urls import path
from . import views

urlpatterns = [
    path('distributiondetails/', views.distribution_detail_list, name='distribution-detail-list'),
    path('distributiondetails/<int:pk>/', views.distribution_detail_detail, name='distribution-detail-detail'),
]
