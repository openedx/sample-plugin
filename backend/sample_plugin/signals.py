"""
Open edX Events signal handlers for the sample_plugin application.

This module demonstrates how to consume Open edX Events (signals) to react to
platform activities and integrate with external systems. Events are part of
the Hooks Extension Framework and provide a stable way to extend Open edX.

What Are Open edX Events?
Events are signals sent when specific actions occur in the platform. Unlike
traditional Django signals, Open edX Events have standardized data structures
and are designed for external consumption.

Key Concepts:
- Events are fired at specific points in the platform lifecycle
- Each event includes structured data (defined in openedx-events)
- Event handlers can perform actions but cannot modify the event data
- Events support both internal processing and external event bus integration

Official Documentation:
- Events Overview: https://docs.openedx.org/projects/openedx-events/en/latest/
- Available Events: https://docs.openedx.org/projects/openedx-events/en/latest/reference/events.html
- Consuming Events: https://docs.openedx.org/projects/openedx-events/en/latest/how-tos/consume-an-event.html
- Hooks Framework: https://docs.openedx.org/en/latest/developers/concepts/hooks_extension_framework.html

Registration Process:
1. Import the event signal from openedx-events
2. Create handler function with correct signature
3. Decorate with @receiver
4. Import this module in apps.py ready() method

Event Data Structure:
Each event defines specific data attributes. Check the event definition in the
official documentation to understand available data:
- Signal Reference: https://docs.openedx.org/projects/openedx-events/en/latest/reference/events.html
- Data Objects: https://docs.openedx.org/projects/openedx-events/en/latest/reference/data.html
- Example: COURSE_CATALOG_INFO_CHANGED provides catalog_info: CourseCatalogData

Common Use Cases:
- Integration with external systems (CRM, analytics, notifications)
- Custom logging and audit trails
- Triggering workflows in other services
- Synchronizing data with external databases
"""

from openedx_events.content_authoring.signals import COURSE_CATALOG_INFO_CHANGED
from openedx_events.content_authoring.data import CourseCatalogData
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

@receiver(COURSE_CATALOG_INFO_CHANGED)
def log_course_info_changed(signal, sender, catalog_info: CourseCatalogData, **kwargs):
    """
    Handle course catalog information changes.

    This function demonstrates how to consume the COURSE_CATALOG_INFO_CHANGED event,
    which is fired whenever course catalog information is updated in the platform.

    Event Trigger Conditions:
    - Course metadata is modified (name, description, etc.)
    - Course schedule is updated
    - Course visibility settings change
    - Other catalog-related modifications

    Args:
        signal: The signal instance that triggered this handler
        sender: The model class that sent the signal
        catalog_info (CourseCatalogData): Structured data about the course
        **kwargs: Additional context parameters

    CourseCatalogData Attributes:
    Based on the official data structure documentation:
    https://docs.openedx.org/projects/openedx-events/en/latest/reference/data.html#openedx_events.content_authoring.data.CourseCatalogData

    - course_key (CourseKey): Unique course identifier
    - name (str): Course display name
    - schedule (CourseScheduleData): Start/end dates and pacing
    - hidden (bool): Course visibility status

    Real-World Use Cases:
    - Sync course metadata with external systems (CRM, marketing sites)
    - Update search indexes when course information changes
    - Trigger email notifications to administrators
    - Log changes for audit and compliance
    - Update analytics dashboards with new course information

    Example Implementation::

        # Send to external CRM system
        external_api.update_course(
            course_id=str(catalog_info.course_key),
            name=catalog_info.name,
            is_hidden=catalog_info.hidden
        )

        # Update internal tracking
        CourseChangeLog.objects.create(
            course_key=catalog_info.course_key,
            change_type='catalog_updated',
            timestamp=timezone.now()
        )

    Performance Considerations:
    - Keep processing lightweight (events should not block platform operations)
    - Use asynchronous tasks for heavy processing (Celery, etc.)
    - Handle exceptions gracefully to prevent platform disruption
    """
    logging.info(f"Course catalog updated: {catalog_info.course_key}")

    # Access available data from the event
    logging.debug(f"Course name: {catalog_info.name}")
    logging.debug(f"Course hidden: {catalog_info.hidden}")

    # Example: Integrate with external systems
    # try:
    #     # Send to external system
    #     external_system.notify_course_update(
    #         course_id=str(catalog_info.course_key),
    #         course_name=catalog_info.name,
    #         is_hidden=catalog_info.hidden
    #     )
    # except Exception as e:
    #     logging.error(f"Failed to notify external system: {e}")

    # Example: Update internal tracking
    # from .models import CourseArchiveStatus
    # CourseArchiveStatus.objects.filter(
    #     course_id=catalog_info.course_key
    # ).update(last_catalog_update=timezone.now())
