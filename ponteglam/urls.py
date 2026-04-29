"""
URL configuration for ponteglam project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

from users.api.views import CustomAuthToken

from companies.api.routers import router as companies_router
from core.api.routers import router as core_router
from services.api.routers import router as services_router
from users.api.routers import router as users_ruoter
from workers.api.routers import router as workers_router


urlpatterns = [
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    path('api-token-auth/', CustomAuthToken.as_view()),
    path('companies/api/', include(companies_router.urls)),
    path('core/api/', include(core_router.urls)),
    path('services/api/', include(services_router.urls)),
    path('users/', include('users.urls')),
    path('users/api/', include(users_ruoter.urls)),
    path('workers/api/', include(workers_router.urls)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
