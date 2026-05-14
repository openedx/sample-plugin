"""
Open edX Events signal handlers for the openedx_plugin_sample application.

This module demonstrates how to consume Open edX Events to react to platform
activity. Events are part of the Hooks Extension Framework and provide a
stable way to extend Open edX without modifying core code.

Key Concepts:
- Events are fired at specific points in the platform lifecycle
- Each event delivers a structured data object (defined in openedx-events)
- Event handlers can take action but cannot modify the event payload
- Handlers must be imported from apps.py ready() so @receiver registers them

Official Documentation:
- Events Overview: https://docs.openedx.org/projects/openedx-events/en/latest/
- Available Events: https://docs.openedx.org/projects/openedx-events/en/latest/reference/events.html
- Consuming Events: https://docs.openedx.org/projects/openedx-events/en/latest/how-tos/consume-an-event.html
- Event Data Objects: https://docs.openedx.org/projects/openedx-events/en/latest/reference/data.html
"""

import logging

from django.dispatch import receiver
from openedx_events.learning.data import CourseEnrollmentData
from openedx_events.learning.signals import COURSE_ENROLLMENT_CHANGED

from .models import CourseArchiveStatus

logger = logging.getLogger(__name__)


@receiver(COURSE_ENROLLMENT_CHANGED)
def unarchive_on_verified_upgrade(
    signal, sender, enrollment: CourseEnrollmentData, **kwargs
):  # pylint: disable=unused-argument
    """
    Unarchive a course on the learner's dashboard when they upgrade to verified.

    If a learner has previously archived a course (CourseArchiveStatus.is_archived=True)
    and then upgrades to the verified track, the course shouldn't stay tucked away
    in their "Archived" section -- their renewed investment in the course is a
    strong signal that they want it back in their active list.

    This is intentionally a one-time nudge, not a continuous rule: if the learner
    re-archives the course later, we respect that choice. That's why we react to
    the enrollment-change *event* rather than computing `isArchivedByLearner`
    from enrollment mode in the filter pipeline.

    Event reference:
    https://docs.openedx.org/projects/openedx-events/en/latest/reference/events.html#openedx_events.learning.signals.COURSE_ENROLLMENT_CHANGED
    """
    if not enrollment.is_active or enrollment.mode != "verified":
        return

    updated = CourseArchiveStatus.objects.filter(
        user_id=enrollment.user.id,
        course_run__course_key=enrollment.course.course_key,
        is_archived=True,
    ).update(is_archived=False, archive_date=None)

    if updated:
        logger.info(
            "Unarchived course %s for user %s after verified upgrade",
            enrollment.course.course_key,
            enrollment.user.id,
        )
