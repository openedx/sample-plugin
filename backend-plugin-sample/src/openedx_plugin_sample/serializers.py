"""
Serializers for the openedx_plugin_sample app.
"""

from django.contrib.auth import get_user_model
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import UsageKey
from openedx_catalog.models import CourseRun
from rest_framework import serializers

from openedx_plugin_sample.models import (
    CourseArchiveStatus,
    CourseAverageRating,
    UnitRating,
    apply_rating_delta,
)

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


class UnitRatingSerializer(serializers.ModelSerializer):
    """
    Serializer for a single learner's rating of a unit.

    Clients send/receive ``usage_key`` as a string; the FK to CourseRun is
    derived server-side from the usage_key's course_key.
    """

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
        required=False,
    )
    usage_key = serializers.CharField(max_length=255)

    class Meta:
        model = UnitRating
        fields = [
            "id",
            "usage_key",
            "stars",
            "user",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def _resolve_course_run(self, usage_key_str):
        """Parse the usage_key and return the owning CourseRun."""
        try:
            usage_key = UsageKey.from_string(usage_key_str)
        except InvalidKeyError as exc:
            raise serializers.ValidationError(
                {"usage_key": f"Invalid usage key: {usage_key_str}"}
            ) from exc
        # @@TODO: in prod, ``CourseRun.objects.get(...)`` and 400 if absent. The
        # POC tolerates missing rows so a fresh dev DB doesn't need to be
        # pre-seeded with every course's CourseRun.
        course_run, _ = CourseRun.objects.get_or_create(
            course_key=str(usage_key.course_key),
        )
        return course_run

    def create(self, validated_data):
        course_run = self._resolve_course_run(validated_data["usage_key"])
        instance = UnitRating.objects.create(course_run=course_run, **validated_data)
        apply_rating_delta(course_run, old_stars=None, new_stars=instance.stars)
        return instance

    def update(self, instance, validated_data):
        old_stars = instance.stars
        # @@TODO: usage_key updates would imply the rating moved to a different
        # unit (and possibly course). POC: ignore changes to usage_key and only
        # respect ``stars`` updates.
        new_stars = validated_data.get("stars", old_stars)
        instance.stars = new_stars
        instance.save(update_fields=["stars", "updated_at"])
        if new_stars != old_stars:
            apply_rating_delta(
                instance.course_run, old_stars=old_stars, new_stars=new_stars,
            )
        return instance


class CourseAverageRatingSerializer(serializers.ModelSerializer):
    """Read-only serializer for the cached per-course rating aggregate."""

    course_id = serializers.SlugRelatedField(
        source="course_run",
        slug_field="course_key",
        read_only=True,
    )

    class Meta:
        model = CourseAverageRating
        fields = [
            "course_id",
            "average_stars",
            "rating_count",
            "sum_stars",
            "updated_at",
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["course_id"] = str(data["course_id"])
        return data
