"""
Open edX Filters implementation for the openedx_plugin_sample application.

This module demonstrates how to use Open edX Filters to modify platform behavior
without changing core code. Filters are part of the Hooks Extension Framework
and allow you to intercept and modify data at specific points in the platform.

What Are Open edX Filters?
Filters are functions that can modify application behavior by altering input data
or halting execution based on specific conditions. Unlike events (which only
observe), filters can change what happens next in the platform.

Key Concepts:
- Filters receive data and return modified data
- They run at specific pipeline steps during platform operations
- Filters can halt execution by raising exceptions
- Multiple filters can be chained together in a pipeline
- Filters should be lightweight and handle errors gracefully

Official Documentation:
- Filters Overview: https://docs.openedx.org/projects/openedx-filters/en/latest/
- Using Filters: https://docs.openedx.org/projects/openedx-filters/en/latest/how-tos/using-filters.html
- Available Filters: https://docs.openedx.org/projects/openedx-filters/en/latest/reference/filters.html
- Filter Tooling: https://docs.openedx.org/projects/openedx-filters/en/latest/reference/filters-tooling.html

Registration Process:
1. Create filter class inheriting from PipelineStep
2. Implement run_filter() method with correct signature
3. Register filter in Django settings OPEN_EDX_FILTERS_CONFIG
4. Deploy and test the filter behavior

Common Use Cases:
- URL redirection and customization
- Access control and permission checks
- Data transformation and validation
- Integration with external systems
- Custom business logic implementation
"""

import logging

import crum
from openedx_filters.filters import PipelineStep

from .models import CourseArchiveStatus, CourseAverageRating

logger = logging.getLogger(__name__)


class AddArchiveStatusToLearnerHomeCourseRun(PipelineStep):
    """
    Customize each courseRun within a Learner Dashboard's /init API response to include the CourseArchiveStatus.
    """  # noqa: E501

    def run_filter(self, serialized_courserun, **kwargs):  # pylint: disable=arguments-differ
        """
        Insert `isArchivedByLearner` into one serialized courseRun for the Learner Home /init response.

        Args:
            serialized_courserun (dict): One courseRun from the serializer. Reads
                `courseId` (a course key string, e.g. "course-v1:edX+DemoX+Demo_Course");
                all other fields are passed through unchanged.

        Returns:
            dict: ``{"serialized_courserun": <updated dict>}``. The updated dict has the
                same keys as the input plus `isArchivedByLearner` (bool) -- True iff a
                CourseArchiveStatus row exists for the current request user and this
                courseId with `is_archived=True`; False otherwise (including when no row
                exists).

        The current user is read from the active request via `crum`, so this filter only
        runs meaningfully inside a request cycle. Note that `isArchivedByLearner` is
        distinct from `isArchived`, which the platform sets based on whether the course
        run itself has ended.
        """  # noqa: E501
        request = crum.get_current_request()
        if not (request and request.user):
            return serialized_courserun
        try:
            is_archived_by_learner = CourseArchiveStatus.objects.get(
                user=request.user,
                course_run__course_key=serialized_courserun["courseId"],
            ).is_archived
        except CourseArchiveStatus.DoesNotExist:
            is_archived_by_learner = False
        return {
            "serialized_courserun": {
                **serialized_courserun,
                "isArchivedByLearner": is_archived_by_learner,
            },
        }


class AddAverageRatingToLearnerHomeCourseRun(PipelineStep):
    """
    Decorate each courseRun in the Learner Home /init response with the cached
    average rating, so the Archive course-card display can render stars without
    a second API call.

    Filter name: ``org.openedx.learning.home.courserun.api.rendered.started.v1``
    """

    def run_filter(self, serialized_courserun, **kwargs):  # pylint: disable=arguments-differ
        """
        Args:
            serialized_courserun (dict): One courseRun from the /init serializer.
                Reads ``courseId``; passes all other fields through unchanged.

        Returns:
            dict: ``{"serialized_courserun": <updated dict>}`` with two new keys
                added:
                  - ``averageStars`` (float or None) -- None when no ratings exist
                  - ``ratingCount`` (int)            -- 0 when no ratings exist
        """
        course_id = serialized_courserun.get("courseId")
        if not course_id:
            return {"serialized_courserun": serialized_courserun}

        # @@TODO: looking up one row per courseRun is fine for a dashboard with a
        # handful of courses but will N+1 on long course lists. A prefetch in
        # the upstream serializer (or a bulk lookup here) would be the prod fix.
        try:
            avg = CourseAverageRating.objects.get(
                course_run__course_key=course_id,
            )
            average_stars = avg.average_stars
            rating_count = avg.rating_count
        except CourseAverageRating.DoesNotExist:
            average_stars = None
            rating_count = 0

        return {
            "serialized_courserun": {
                **serialized_courserun,
                "averageStars": average_stars,
                "ratingCount": rating_count,
            },
        }
