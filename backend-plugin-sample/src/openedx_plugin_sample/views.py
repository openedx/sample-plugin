"""
Views for the openedx_plugin_sample app.
"""

import logging

from django.utils import timezone
from django_filters import rest_framework as django_filters
from django_filters.rest_framework import DjangoFilterBackend
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle

from openedx_plugin_sample.models import (
    CourseArchiveStatus,
    CourseAverageRating,
    UnitRating,
    apply_rating_delta,
)
from openedx_plugin_sample.serializers import (
    CourseArchiveStatusSerializer,
    CourseAverageRatingSerializer,
    UnitRatingSerializer,
)

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


class CourseArchiveStatusFilterSet(django_filters.FilterSet):
    """
    FilterSet for CourseArchiveStatus.

    The model stores a FK to CourseRun, but the public API filters and orders
    by the course_key string (never by the internal CourseRun PK).
    """

    # Map ?course_id=course-v1:... onto the FK's course_key column.
    course_id = django_filters.CharFilter(field_name="course_run__course_key")

    # Expose ?ordering=course_id (and other fields) without leaking the
    # double-underscore FK lookup path.
    ordering = django_filters.OrderingFilter(
        fields=(
            ("course_run__course_key", "course_id"),
            ("user", "user"),
            ("is_archived", "is_archived"),
            ("archive_date", "archive_date"),
            ("created_at", "created_at"),
            ("updated_at", "updated_at"),
        )
    )

    class Meta:
        """
        FilterSet Meta options for CourseArchiveStatus.
        """

        model = CourseArchiveStatus
        fields = ["course_id", "user", "is_archived"]


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
    throttle_classes = [
        CourseArchiveStatusThrottle,
    ]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = CourseArchiveStatusFilterSet
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

        # Always use select_related to avoid N+1 queries when accessing
        # related user and course_run (for course_key) fields.
        base_queryset = CourseArchiveStatus.objects.select_related("user", "course_run")

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

        Validates permission for user override and sets archive_date if needed.
        """
        # Check if user was explicitly provided and differs from current user
        if "user" in self.request.data:
            requested_user_id = self.request.data["user"]
            if requested_user_id != self.request.user.id and not (
                self.request.user.is_staff or self.request.user.is_superuser
            ):
                logger.warning(
                    "Permission denied: User %s tried to create a record for user %s",
                    self.request.user.username,
                    requested_user_id,
                )
                raise PermissionDenied(
                    "You do not have permission to create records for other users."
                )

        # Set archive_date if is_archived is True
        data = {}
        if serializer.validated_data.get("is_archived", False):
            data["archive_date"] = timezone.now()

        # Create the record
        instance = serializer.save(**data)

        # Log at debug level for normal operation
        logger.debug(
            "CourseArchiveStatus created: course_id=%s, user=%s, is_archived=%s",
            instance.course_run.course_key,
            instance.user.username,
            instance.is_archived,
        )

        return instance

    def perform_update(self, serializer):
        """
        Perform update of an existing CourseArchiveStatus.

        Validates permission for user override and updates archive_date if needed.
        """
        instance = serializer.instance

        # Check if user was explicitly provided and differs from current user
        if "user" in self.request.data:
            requested_user_id = self.request.data["user"]
            if requested_user_id != self.request.user.id and not (
                self.request.user.is_staff or self.request.user.is_superuser
            ):
                logger.warning(
                    "Permission denied: User %s tried to update a record for user %s",
                    self.request.user.username,
                    requested_user_id,
                )
                raise PermissionDenied(
                    "You do not have permission to update records for other users."
                )

        # Handle archive_date if is_archived changes
        data = {}
        if "is_archived" in serializer.validated_data:
            # If changing from not archived to archived
            if serializer.validated_data["is_archived"] and not instance.is_archived:
                data["archive_date"] = timezone.now()
            # If changing from archived to not archived
            elif not serializer.validated_data["is_archived"] and instance.is_archived:
                data["archive_date"] = None

        # Update the record
        updated_instance = serializer.save(**data)

        # Log at debug level
        logger.debug(
            "CourseArchiveStatus updated: course_id=%s, user=%s, is_archived=%s",
            updated_instance.course_run.course_key,
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
            instance.course_run.course_key,
            instance.user.username,
            self.request.user.username,
        )

        # Delete the instance
        return super().perform_destroy(instance)


class UnitRatingPagination(PageNumberPagination):
    """Pagination for UnitRating list/CourseAverageRating list."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class UnitRatingThrottle(UserRateThrottle):
    """Throttle for the UnitRating API."""

    rate = "60/minute"


class UnitRatingFilterSet(django_filters.FilterSet):
    """
    Public filters map onto the user-friendly fields rather than FK PKs.
    """

    # ?course_id=course-v1:... -> course_run.course_key
    course_id = django_filters.CharFilter(field_name="course_run__course_key")

    ordering = django_filters.OrderingFilter(
        fields=(
            ("usage_key", "usage_key"),
            ("stars", "stars"),
            ("created_at", "created_at"),
            ("updated_at", "updated_at"),
        )
    )

    class Meta:
        model = UnitRating
        fields = ["usage_key", "course_id", "user", "stars"]


class UnitRatingViewSet(viewsets.ModelViewSet):
    """
    Per-unit rating CRUD.

    GET /unit-rating/?usage_key=<key>  -> the caller's rating for that unit
    POST /unit-rating/                 -> create a new rating
    PATCH /unit-rating/<id>/           -> update an existing rating
    DELETE /unit-rating/<id>/          -> remove a rating

    Regular users only see their own rows; staff/superusers see all.
    """

    serializer_class = UnitRatingSerializer
    permission_classes = [IsOwnerOrStaffSuperuser]
    pagination_class = UnitRatingPagination
    throttle_classes = [UnitRatingThrottle]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = UnitRatingFilterSet
    ordering = ["-updated_at"]

    def get_queryset(self):
        user = self.request.user
        qs = UnitRating.objects.select_related("user", "course_run")
        if user.is_staff or user.is_superuser:
            return qs
        return qs.filter(user=user)

    def perform_create(self, serializer):
        # Block users from creating rows on behalf of other users.
        if "user" in self.request.data:
            requested_user_id = self.request.data["user"]
            if requested_user_id != self.request.user.id and not (
                self.request.user.is_staff or self.request.user.is_superuser
            ):
                raise PermissionDenied(
                    "You do not have permission to create ratings for other users."
                )
        # The serializer's create() handles the aggregate update.
        serializer.save()

    def perform_update(self, serializer):
        if "user" in self.request.data:
            requested_user_id = self.request.data["user"]
            if requested_user_id != self.request.user.id and not (
                self.request.user.is_staff or self.request.user.is_superuser
            ):
                raise PermissionDenied(
                    "You do not have permission to update ratings for other users."
                )
        serializer.save()

    def perform_destroy(self, instance):
        # Decrement the cached aggregate before deleting the row.
        apply_rating_delta(
            instance.course_run,
            old_stars=instance.stars,
            new_stars=None,
        )
        super().perform_destroy(instance)


class CourseAverageRatingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    Read-only access to the cached per-course rating aggregate.

    Mostly useful for debugging / admin. The frontend reads the same data off
    the Learner Home /init response via the filter pipeline rather than calling
    this endpoint directly.
    """

    serializer_class = CourseAverageRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = UnitRatingPagination
    queryset = CourseAverageRating.objects.select_related("course_run").all()
    # Look up by course_key string rather than internal PK.
    lookup_field = "course_run__course_key"
    lookup_url_kwarg = "course_id"
    # @@TODO: courseId strings contain ':' and '+' which trip up default DRF
    # URL routing. Either set a custom regex on the route or expose an
    # ``?course_id=`` filter instead.
