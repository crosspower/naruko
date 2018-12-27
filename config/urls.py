"""ebdjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.contrib import admin
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token, refresh_jwt_token
from backend.urls import tenant_router, router, aws_router, resource_router, region_router, service_router
from backend.views.reset_password_view import reset_password
from backend.views.notify_view import notify
from backend.views.event_execute_view import event_execute

api_urlpatterns = [
    path('auth/', obtain_jwt_token),
    path('auth/refresh/', refresh_jwt_token),
    path('auth/verify/', verify_jwt_token),
    path('auth/reset/', reset_password),
    path('notify/', notify),
    path('event/', event_execute),
    path('', include(router.urls)),
    path('', include(tenant_router.urls)),
    path('', include(aws_router.urls)),
    path('', include(region_router.urls)),
    path('', include(service_router.urls)),
    path('', include(resource_router.urls))
]

urlpatterns = [
    path('api/', include(api_urlpatterns)),
    path('admin/', admin.site.urls),
    path('', include('backend.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
