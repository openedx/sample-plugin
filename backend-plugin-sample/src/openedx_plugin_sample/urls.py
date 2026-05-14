"""
URLs for openedx_plugin_sample.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from openedx_plugin_sample.views import (
    CourseArchiveStatusViewSet,
    CourseAverageRatingViewSet,
    UnitRatingViewSet,
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(
    r"course-archive-status",
    CourseArchiveStatusViewSet,
    basename="course-archive-status",
)
router.register(r"unit-rating", UnitRatingViewSet, basename="unit-rating")
# @@TODO: CourseAverageRating detail-by-course_key needs a custom URL or query
# filter; for now only the list endpoint is meaningfully usable.
router.register(
    r"course-average-rating",
    CourseAverageRatingViewSet,
    basename="course-average-rating",
)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path("api/v1/", include(router.urls)),
]
