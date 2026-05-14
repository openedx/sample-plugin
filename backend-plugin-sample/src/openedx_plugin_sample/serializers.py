"""
Serializers for the openedx_plugin_sample app.
"""

from django.contrib.auth import get_user_model
from openedx_catalog.models import CourseRun
from rest_framework import serializers

from openedx_plugin_sample.models import CourseArchiveStatus

User = get_user_model()


class CourseArchiveStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for the CourseArchiveStatus model.
    """

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
        required=False,
    )

    # The model stores a FK to CourseRun, but APIs should identify courses by
    # their full course key string (e.g. "course-v1:edX+DemoX+Demo_Course"),
    # never by CourseRun's internal integer PK. The slug field looks up the
    # related CourseRun by its `course_key` for both reads and writes.
    course_id = serializers.SlugRelatedField(
        source="course_run",
        slug_field="course_key",
        queryset=CourseRun.objects.all(),
    )

    class Meta:
        """
        Meta class for CourseArchiveStatusSerializer.
        """

        model = CourseArchiveStatus
        fields = [
            "id",
            "course_id",
            "user",
            "is_archived",
            "archive_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "archive_date"]

    def to_representation(self, instance):
        """
        Serialize the instance, casting course_id to a string.

        CourseRun.course_key returns a CourseLocator (not a string), which the
        default JSON encoder can't serialize, so we coerce to str on output.
        """
        data = super().to_representation(instance)
        data["course_id"] = str(data["course_id"])
        return data
