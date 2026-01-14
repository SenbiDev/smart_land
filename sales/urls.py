from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_sale, name='list-sale'),
    path('create/', views.create_sale, name='create-sale'),
    path('<int:pk>/', views.sale_detail, name='detail-sale'),
]