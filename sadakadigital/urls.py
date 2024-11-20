"""
URL configuration for sadakadigital project.

The `urlpatterns` list routes URLs to operations. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function operations
    1. Add an import:  from my_app import operations
    2. Add a URL to urlpatterns:  path('', operations.home, name='home')
Class-based operations
    1. Add an import:  from other_app.operations import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from sadakadigital import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/user-management/', include('user_management.urls')),
    path('api/v1/service-providers/', include('service_providers.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
