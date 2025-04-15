"""
URLs for sample_plugin.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from sample_plugin.views import CourseArchiveStatusViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(
    r"course-archive-status",
    CourseArchiveStatusViewSet,
    basename="course-archive-status",
)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path("api/v1/", include(router.urls)),
]
