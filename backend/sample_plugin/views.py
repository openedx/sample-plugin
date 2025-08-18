"""
Views for the sample_plugin app.
"""

import logging

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from rest_framework import filters, permissions, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle

from sample_plugin.models import CourseArchiveStatus
from sample_plugin.serializers import CourseArchiveStatusSerializer

logger = logging.getLogger(__name__)


class IsOwnerOrStaffSuperuser(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or staff/superusers to view or edit it.
    """

    def has_permission(self, request, view):
        """
        Return True if permission is granted to the view.
        """
        # Allow authenticated users to list and create
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Return True if permission is granted to the object.
        """
        # Allow if the object belongs to the requesting user
        if obj.user == request.user:
            return True

        # Allow staff users and superusers
        if request.user.is_staff or request.user.is_superuser:
            return True

        return False


class CourseArchiveStatusPagination(PageNumberPagination):
    """
    Pagination class for CourseArchiveStatus.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class CourseArchiveStatusThrottle(UserRateThrottle):
    """
    Throttle for the CourseArchiveStatus API.
    """

    rate = "60/minute"


class CourseArchiveStatusViewSet(viewsets.ModelViewSet):
    """
    API viewset for CourseArchiveStatus.

    Allows users to view their own course archive statuses and staff/superusers to view all.
    Pagination is applied with a default page size of 20 (max 100).
    Filtering is available on course_id, user, and is_archived fields.
    Ordering is available on all fields.
    """

    serializer_class = CourseArchiveStatusSerializer
    permission_classes = [IsOwnerOrStaffSuperuser]
    pagination_class = CourseArchiveStatusPagination
    throttle_classes = [CourseArchiveStatusThrottle, ]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["course_id", "user", "is_archived"]
    ordering_fields = [
        "course_id",
        "user",
        "is_archived",
        "archive_date",
        "created_at",
        "updated_at",
    ]
    ordering = ["-updated_at"]

    def get_queryset(self):
        """
        Return the queryset for this viewset.

        Regular users can only see their own records.
        Staff and superusers can see all records but with optimized queries.
        """
        user = self.request.user

        # Validate query parameters to prevent injection
        self._validate_query_params()

        # Always use select_related to avoid N+1 queries
        base_queryset = CourseArchiveStatus.objects.select_related("user")

        if user.is_staff or user.is_superuser:
            return base_queryset

        # Regular users only see their own records
        return base_queryset.filter(user=user)

    def _validate_query_params(self):
        """
        Validate query parameters to prevent injection.
        """
        # Example validation for course_id format
        course_id = self.request.query_params.get("course_id")
        if course_id and not self._is_valid_course_id(course_id):
            logger.warning(
                "Invalid course_id in request: %s, user: %s",
                course_id,
                self.request.user.username,
            )
            raise ValidationError({"course_id": "Invalid course ID format."})

    def _is_valid_course_id(self, course_id):
        """
        Check if the course_id is in a valid format.

        This is a basic implementation - in production, you might use a more
        sophisticated validator from the edx-platform.
        """
        try:
            CourseKey.from_string(course_id)
            return True
        except InvalidKeyError:
            return False

    def perform_create(self, serializer):
        """
        Perform creation of a new CourseArchiveStatus.

        Sets the user to the requesting user if not specified.
        Sets archive_date and archived_by if is_archived is True.
        """
        data = serializer.validated_data.copy()

        # Set user to requesting user if not specified
        if "user" not in data:
            data["user"] = self.request.user
        # Only allow staff/superusers to create records for other users
        elif data["user"] != self.request.user and not (
            self.request.user.is_staff or self.request.user.is_superuser
        ):
            logger.warning(
                "Permission denied: User %s tried to create a record for user %s",
                self.request.user.username,
                data["user"].username,
            )
            raise PermissionDenied(
                "You do not have permission to create records for other users."
            )

        # Set archive_date if is_archived is True
        if data.get("is_archived", False):
            data["archive_date"] = timezone.now()

        # Create the record
        instance = serializer.save(**data)

        # Log at debug level for normal operation
        logger.debug(
            "CourseArchiveStatus created: course_id=%s, user=%s, is_archived=%s",
            instance.course_id,
            instance.user.username,
            instance.is_archived,
        )

        return instance

    def perform_update(self, serializer):
        """
        Perform update of an existing CourseArchiveStatus.

        Updates archive_date and archived_by if is_archived changes.
        """
        instance = serializer.instance
        data = serializer.validated_data.copy()

        # Handle archive_date if is_archived changes
        if "is_archived" in data:
            # If changing from not archived to archived
            if data["is_archived"] and not instance.is_archived:
                data["archive_date"] = timezone.now()
            # If changing from archived to not archived
            elif not data["is_archived"] and instance.is_archived:
                data["archive_date"] = None

        # Update the record
        updated_instance = serializer.save(**data)

        # Log at debug level
        logger.debug(
            "CourseArchiveStatus updated: course_id=%s, user=%s, is_archived=%s",
            updated_instance.course_id,
            updated_instance.user.username,
            updated_instance.is_archived,
        )

        return updated_instance

    def perform_destroy(self, instance):
        """
        Perform deletion of an existing CourseArchiveStatus.
        """
        # Log at debug level before deletion
        logger.debug(
            "CourseArchiveStatus deleted: course_id=%s, user=%s, by=%s",
            instance.course_id,
            instance.user.username,
            self.request.user.username,
        )

        # Delete the instance
        return super().perform_destroy(instance)
