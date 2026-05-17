"""
Database models for openedx_plugin_sample.

Two independent features live side-by-side in this app:

* ``CourseArchiveStatus`` -- per-learner "this course is archived" flag,
  consumed by the Learner Dashboard course-card listing.
* ``UnitRating`` + ``CourseAverageRating`` -- learners optionally rate units
  1-5 stars; we keep a cached per-course average that is updated incrementally
  on each write and fully recomputed when a course is republished.
"""

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import Count, Sum
from opaque_keys.edx.django.models import UsageKeyField
from openedx_catalog.models import CourseRun


class CourseArchiveStatus(models.Model):
    """
    Model to track the archive status of a course.

    Stores information about whether a course has been archived and when it was archived.

    .. no_pii: This model does not store PII directly, only references to users via foreign keys.
    """

    course_run = models.ForeignKey(
        CourseRun,
        on_delete=models.CASCADE,
        related_name="archive_statuses",
        help_text="The course run that this archive status is for.",
    )

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="course_archive_statuses",
        help_text="The user who this archive status is for.",
    )

    is_archived = models.BooleanField(
        default=False,
        db_index=True,  # Add index for performance on this frequently filtered field
        help_text="Whether the course is archived.",
    )

    archive_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The date and time when the course was archived.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Return a string representation of the course archive status.
        """
        # pylint: disable=no-member
        # Identify the course by its course_key string, never by the internal PK.
        archived = "Archived" if self.is_archived else "Not Archived"
        return f"{self.course_run.course_key} - {self.user.username} - {archived}"

    class Meta:
        """
        Meta options for the CourseArchiveStatus model.
        """

        verbose_name = "Course Archive Status"
        verbose_name_plural = "Course Archive Statuses"
        ordering = ["-updated_at"]
        # Ensure combination of course_run and user is unique
        constraints = [
            models.UniqueConstraint(
                fields=["course_run", "user"], name="unique_user_course_archive_status"
            )
        ]


class UnitRating(models.Model):
    """
    A single learner's 1-5 star rating of one unit (vertical block).

    .. no_pii: Stores no PII directly, only FKs to user and course_run.
    """

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="unit_ratings",
    )
    course_run = models.ForeignKey(
        CourseRun,
        on_delete=models.CASCADE,
        related_name="unit_ratings",
        help_text="Denormalized from usage_key so we can aggregate per course cheaply.",
    )
    usage_key = UsageKeyField(
        max_length=255,
        db_index=True,
        help_text="e.g. 'block-v1:edX+DemoX+Demo_Course+type@vertical+block@abc123'",
    )
    stars = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "usage_key"],
                name="unique_user_unit_rating",
            ),
        ]
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.username} rated {self.usage_key}: {self.stars}*"


class CourseAverageRating(models.Model):
    """
    Cached aggregate of all UnitRatings for a CourseRun.

    Kept in sync incrementally by ``apply_rating_delta`` (called from the API on
    create/update/destroy) and fully recomputed by ``recompute_from_scratch``
    on course publish.

    .. no_pii: Aggregate only, no per-user data.
    """

    course_run = models.OneToOneField(
        CourseRun,
        on_delete=models.CASCADE,
        related_name="average_rating",
    )
    # Stored sum + count enables O(1) incremental updates without re-aggregating.
    sum_stars = models.PositiveIntegerField(default=0)
    rating_count = models.PositiveIntegerField(default=0)
    average_stars = models.FloatField(
        null=True,
        blank=True,
        help_text="Null when rating_count == 0.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.rating_count == 0:
            return f"{self.course_run.course_key}: no ratings yet"
        return (
            f"{self.course_run.course_key}: {self.average_stars:.2f}* "
            f"({self.rating_count} ratings)"
        )

    def _refresh_average(self):
        """Recompute ``average_stars`` from current ``sum_stars`` / ``rating_count``."""
        if self.rating_count == 0:
            self.average_stars = None
        else:
            self.average_stars = self.sum_stars / self.rating_count

    def recompute_from_scratch(self, allowed_usage_keys=None):
        """
        Rebuild sum/count/average by scanning UnitRating rows for this course_run.

        Args:
            allowed_usage_keys: Optional iterable of usage_keys to restrict the
                aggregation to. Intended for the publish handler so that
                ratings for units that have since been removed are excluded.
                If None, all UnitRating rows for the course_run are included.
        """
        qs = UnitRating.objects.filter(course_run=self.course_run)
        if allowed_usage_keys is not None:
            qs = qs.filter(usage_key__in=list(allowed_usage_keys))
        agg = qs.aggregate(total=Sum("stars"), n=Count("id"))
        self.sum_stars = agg["total"] or 0
        self.rating_count = agg["n"] or 0
        self._refresh_average()
        self.save()


def apply_rating_delta(course_run, *, old_stars, new_stars):
    """
    Update the cached CourseAverageRating to reflect a single rating change.

    Pass ``old_stars=None`` for a brand-new rating, ``new_stars=None`` for a
    deletion, or both non-None for an update.

    Wrapped in ``transaction.atomic`` + ``select_for_update`` so concurrent
    rating writes against the same course don't race on the cached aggregate.
    """
    if old_stars is None and new_stars is None:
        return

    with transaction.atomic():
        avg, _ = CourseAverageRating.objects.select_for_update().get_or_create(
            course_run=course_run,
        )
        if old_stars is None:
            avg.sum_stars += new_stars
            avg.rating_count += 1
        elif new_stars is None:
            avg.sum_stars = max(0, avg.sum_stars - old_stars)
            avg.rating_count = max(0, avg.rating_count - 1)
        else:
            avg.sum_stars = max(0, avg.sum_stars - old_stars) + new_stars
        avg._refresh_average()
        avg.save()
