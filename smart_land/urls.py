"""
URL configuration for smart_land project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('authentication.urls')),
    path('api/investor/', include('investor.urls')),
    path('api/', include('asset.urls')),
    path('api/fundingsource/', include('funding_source.urls')),
    path('api/funding/', include('funding.urls')),
    path('api/ownership/', include('ownership.urls')),
    path('api/production/', include('production.urls')),
    path('api/profit-distribution/', include('profit_distribution.urls')),
    path('api/', include('project.urls')),
    path('api/expense/', include('expense.urls')),
]
