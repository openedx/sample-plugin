"""
Open edX Filters implementation for the sample_plugin application.

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
"""  # pylint: disable=line-too-long

import logging
import re

from openedx_filters.filters import PipelineStep

logger = logging.getLogger(__name__)


class ChangeCourseAboutPageUrl(PipelineStep):
    """
    Filter to customize course about page URLs.

    This filter demonstrates how to intercept and modify course about page URLs,
    redirecting them to external sites or custom implementations.

    Filter Hook Point:
    This filter hooks into the course about page URL rendering process.
    Register it for the filter: org.openedx.learning.course.about.render.started.v1

    Registration Example (in settings/common.py)::

        def plugin_settings(settings):
            settings.OPEN_EDX_FILTERS_CONFIG = {
                "org.openedx.learning.course.about.render.started.v1": {
                    "pipeline": [
                        "sample_plugin.pipeline.ChangeCourseAboutPageUrl"
                    ],
                    "fail_silently": False,
                }
            }

    Filter Documentation:
    - Available Filters: https://docs.openedx.org/projects/openedx-filters/en/latest/reference/filters.html
    - PipelineStep: https://docs.openedx.org/projects/openedx-filters/en/latest/reference/filters-tooling.html#openedx_filters.filters.PipelineStep

    Real-World Use Cases:
    - Redirect to marketing site course pages
    - Implement custom course discovery interfaces
    - Add tracking parameters to URLs
    - Route different course types to different platforms
    - Implement A/B testing for course pages
    """  # noqa: E501

    def run_filter(self, url, org, **kwargs):  # pylint: disable=arguments-differ
        """
        Modify the course about page URL.

        This method intercepts course about page URL generation and can modify
        the destination URL based on business logic.

        Args:
            url (str): The original course about page URL
            org (str): The organization/institution identifier
            **kwargs: Additional context data from the platform

        Returns:
            dict: Dictionary with same parameter names as input
                - url (str): Modified or original URL
                - org (str): Organization identifier (usually unchanged)

        Raises:
            FilterException: If processing should be halted

        Filter Requirements:
        - Must return dictionary with keys matching input parameters
        - Return None to skip this filter (let other filters run)
        - Raise FilterException to halt pipeline execution
        - Handle all input scenarios gracefully

        URL Pattern Matching:
        This implementation looks for Open edX course keys in the format:
        course-v1:ORG+COURSE+RUN (e.g., course-v1:edX+DemoX+Demo_Course)

        Documentation:
        - run_filter method: https://docs.openedx.org/projects/openedx-filters/en/latest/reference/filters-tooling.html#openedx_filters.filters.PipelineStep.run_filter
        """  # noqa: E501
        # Extract course ID using Open edX course key pattern
        # Course keys follow the format: course-v1:ORG+COURSE+RUN
        pattern = r'(?P<course_id>course-v1:[^/]+)'

        match = re.search(pattern, url)
        if match:
            course_id = match.group('course_id')

            # Example: Redirect to external marketing site
            new_url = f"https://example.com/new_about_page/{course_id}"

            logger.debug(
                f"Redirecting course about page for {course_id} from {url} to {new_url}"
            )

            # Return modified data
            return {"url": new_url, "org": org}

        # No course ID found - return original data unchanged
        logger.debug(f"No course ID found in URL {url}, leaving unchanged")
        return {"url": url, "org": org}

        # Alternative patterns for different business logic:

        # Organization-based routing:
        # if org == "special_org":
        #     new_url = f"https://special-site.com/courses/{course_id}"
        #     return {"url": new_url, "org": org}

        # Course type-based routing:
        # if "MicroMasters" in course_id:
        #     new_url = f"https://micromasters.example.com/{course_id}"
        #     return {"url": new_url, "org": org}

        # A/B testing implementation:
        # import random
        # if random.choice([True, False]):
        #     new_url = f"https://variant-a.example.com/{course_id}"
        # else:
        #     new_url = f"https://variant-b.example.com/{course_id}"
        # return {"url": new_url, "org": org}
