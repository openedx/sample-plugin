#!/usr/bin/env python
# pylint: disable=redefined-outer-name
"""
Tests for the `sample-plugin` Open edX Filters pipeline steps.
"""

from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model
from opaque_keys.edx.keys import CourseKey

from openedx_plugin_sample.models import CourseArchiveStatus
from openedx_plugin_sample.pipeline import AddArchiveStatusToLearnerHomeCourseRun

User = get_user_model()


@pytest.fixture
def user():
    """
    Create and return a test user.
    """
    return User.objects.create_user(
        username="testuser", email="testuser@example.com", password="password123"
    )


@pytest.fixture
def course_key():
    """
    Create and return a test course key.
    """
    return CourseKey.from_string("course-v1:edX+DemoX+Demo_Course")


@pytest.fixture
def serialized_courserun(course_key):
    """
    Return a minimal courseRun dict like the learner home /init API would emit.
    """
    return {
        "courseId": str(course_key),
        "courseNumber": "DemoX",
    }


@pytest.fixture
def mock_current_request(user):
    """
    Patch crum.get_current_request so the filter sees `user` as the requester.

    The filter relies on `crum` to find the current user, which is set by middleware
    in a real request cycle. In unit tests we stub it directly.
    """
    request = MagicMock()
    request.user = user
    with patch(
        "openedx_plugin_sample.pipeline.crum.get_current_request",
        return_value=request,
    ):
        yield request


@pytest.mark.django_db
def test_archived_courserun_gets_is_archived_by_learner_true(
    user, course_key, serialized_courserun, mock_current_request  # pylint: disable=unused-argument
):
    """
    Test that the filter adds isArchivedByLearner=True when the learner has
    archived this course.
    """
    CourseArchiveStatus.objects.create(
        course_id=course_key, user=user, is_archived=True
    )

    result = AddArchiveStatusToLearnerHomeCourseRun(
        filter_type="org.openedx.learning.home.courserun.api.rendering.started.v1",
        running_pipeline=[],
    ).run_filter(serialized_courserun=serialized_courserun)

    assert result["serialized_courserun"]["isArchivedByLearner"] is True
    # Existing fields on the courseRun are preserved.
    assert result["serialized_courserun"]["courseId"] == str(course_key)
    assert result["serialized_courserun"]["courseNumber"] == "DemoX"


@pytest.mark.django_db
def test_courserun_with_no_archive_record_defaults_to_false(
    serialized_courserun, mock_current_request  # pylint: disable=unused-argument
):
    """
    Test that the filter defaults isArchivedByLearner to False when the learner
    has no CourseArchiveStatus row for the course.
    """
    result = AddArchiveStatusToLearnerHomeCourseRun(
        filter_type="org.openedx.learning.home.courserun.api.rendering.started.v1",
        running_pipeline=[],
    ).run_filter(serialized_courserun=serialized_courserun)

    assert result["serialized_courserun"]["isArchivedByLearner"] is False
