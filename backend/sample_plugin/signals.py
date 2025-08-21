"""
Signal handlers for the sample_plugin application.

Possible signals you can listen to from the edx-platform repo are defined in the openedx-events repo. You can listen to
those signals from this file which gets read as a part of django startup due to it being imported in the ready()
function in apps.py

Useful Links:

- openedx-events docs: https://docs.openedx.org/projects/openedx-events/en/latest/index.html
- openedx-events list of events: https://docs.openedx.org/projects/openedx-events/en/latest/reference/events.html
- how to consume events: https://docs.openedx.org/projects/openedx-events/en/latest/how-tos/consume-an-event.html

Note: Different signals send different params to the called function so you need to look at the `data` attribute in the
signal definition to know what named params are getting sent and what the data in those objects is going to be.
"""

from openedx_events.content_authoring.signals import COURSE_CATALOG_INFO_CHANGED
from openedx_events.content_authoring.data import CourseCatalogData
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

@receiver(COURSE_CATALOG_INFO_CHANGED)
def log_course_info_changed(signal, sender, catalog_info: CourseCatalogData, **kwargs):
    logging.info(f"{catalog_info.course_key} has been updated!")

    # Then you could take some action related to your personal systems here
