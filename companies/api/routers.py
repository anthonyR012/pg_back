"""
File for the API routes of the companies application
"""

# Third-party Libraries
from rest_framework import routers

# Local Modules
from companies.api import views


router = routers.DefaultRouter()

router.register(
    r'create-company', views.CreateCompany, basename='create-company'
)
router.register(
    r'create-headquarter', views.CreateHeadquarter,
    basename='create-headquarter'
)
router.register(
    r'create-week-day-time-configuration-company',
    views.CreateWeekDayTimeConfigurationCompany,
    basename='create-week-day-time-configuration-company'
)
router.register(
    r'list-companies', views.ListCompanies, basename='list-companies'
)
router.register(
    r'headquarter-like', views.HeadquarterLike,
    basename='headquarter-like'
)
router.register(
    r'headquarter-dislike', views.HeadquarterDislike,
    basename='headquarter-dislike'
)
