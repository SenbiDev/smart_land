from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvestorListCreateView, InvestorDetailView

urlpatterns = [
    path('', InvestorListCreateView.as_view(), name='investor-list-create'),
    path('<int:pk>/', InvestorDetailView.as_view(), name='investor-detail'),
]
