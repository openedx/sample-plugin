"""
Django admin configuration for openedx_plugin_sample.

This module demonstrates how to expose plugin models in the Django admin
site provided by Open edX (LMS and CMS each have their own admin under
``/admin/``). Defining a ``ModelAdmin`` for each model gives operators a
ready-made UI to inspect and manage plugin data without needing custom
tooling.

Django Documentation:
- ModelAdmin: https://docs.djangoproject.com/en/stable/ref/contrib/admin/
"""

from django.contrib import admin

from openedx_plugin_sample.models import CourseArchiveStatus


@admin.register(CourseArchiveStatus)
class CourseArchiveStatusAdmin(admin.ModelAdmin):
    """
    Admin configuration for the CourseArchiveStatus model.
    """

    list_display = (
        "course_key",
        "user",
        "is_archived",
        "archive_date",
        "updated_at",
    )
    list_filter = ("is_archived",)
    # Search by the related CourseRun's course_key and the user's username/email.
    search_fields = (
        "course_run__course_key",
        "user__username",
        "user__email",
    )
    # FKs use raw id widgets (lookup popup) rather than a <select>, since the
    # CourseRun and User tables can have many thousands of rows on a real
    # Open edX deployment.
    raw_id_fields = ("course_run", "user")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-updated_at",)

    @admin.display(description="Course key", ordering="course_run__course_key")
    def course_key(self, obj: CourseArchiveStatus) -> str:
        """
        Show the course's course_key string in list_display.

        We never expose CourseRun's internal integer PK in the admin; the
        course_key (e.g. "course-v1:edX+DemoX+Demo_Course") is the identifier
        operators recognize.
        """
        return str(obj.course_run.course_key)
