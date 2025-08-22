import logging
import re

from openedx_filters.filters import PipelineStep

logger = logging.getLogger(__name__)


class ChangeCourseAboutPageUrl(PipelineStep):
    def run_filter(self, url, org, **kwargs):
        """
        The `run_filter` function must return eiter a dictonary with keys matching the names of the params passed in, or
        none.  More info can be found in the run_filter base docs:
            https://docs.openedx.org/projects/openedx-filters/en/latest/reference/filters-tooling.html#openedx_filters.filters.PipelineStep.run_filter
        """

        # Extract the course ID from the existing URL
        pattern = r'(?P<course_id>course-v1:[^/]+)'

        match = re.search(pattern, url)
        if match:
            course_id = match.group('course_id')
            new_url = f"https://example.com/new_about_page/{course_id}"
            logging.debug(f"Replacing old course about url for {course_id} with a different site.")
            return {"url": new_url, "org": org}

        data = {"url": url, "org": org}
        return data
