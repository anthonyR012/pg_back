"""
File for the API routes of the services application
"""

# Third-party Libraries
from rest_framework import routers

# Local Modules
from services.api import views


router = routers.DefaultRouter()

router.register(
    r'create-service', views.CreateService, basename='create-service'
)
router.register(
    r'list-services', views.ListServices, basename='list-services'
)
router.register(
    r'list-categories-services', views.ListCategoriesServices,
    basename='list-categories-services'
)
