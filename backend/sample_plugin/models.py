"""
Database models for sample_plugin.
"""
from django.contrib.auth import get_user_model
from django.db import models
from opaque_keys.edx.django.models import CourseKeyField


class CourseArchiveStatus(models.Model):
    """
    Model to track the archive status of a course.

    Stores information about whether a course has been archived and when it was archived.
    
    .. no_pii: This model does not store PII directly, only references to users via foreign keys.
    """

    course_id = CourseKeyField(
        max_length=255,
        db_index=True,
        help_text="The unique identifier for the course."
    )

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="course_archive_statuses",
        help_text="The user who this archive status is for."
    )

    is_archived = models.BooleanField(
        default=False,
        db_index=True,  # Add index for performance on this frequently filtered field
        help_text="Whether the course is archived."
    )

    archive_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The date and time when the course was archived."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Return a string representation of the course archive status.
        """
        return f"{self.course_id} - {self.user.username} - {'Archived' if self.is_archived else 'Not Archived'}"

    class Meta:
        """
        Meta options for the CourseArchiveStatus model.
        """
        verbose_name = "Course Archive Status"
        verbose_name_plural = "Course Archive Statuses"
        ordering = ["-updated_at"]
        # Ensure combination of course_id and user is unique
        constraints = [
            models.UniqueConstraint(
                fields=['course_id', 'user'],
                name='unique_user_course_archive_status'
            )
        ]
