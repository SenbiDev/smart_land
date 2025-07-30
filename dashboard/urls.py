from django.urls import path
from .views import Dashboard

urlpatterns = [
    path('dashboards/', Dashboard, name='dashboard'),
]
