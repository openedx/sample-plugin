#!/usr/bin/env python
# pylint: disable=redefined-outer-name
"""
Tests for the `sample-plugin` Open edX Events signal handlers.
"""

from datetime import datetime, timezone

import pytest
from django.contrib.auth import get_user_model
from opaque_keys.edx.keys import CourseKey
from openedx_events.learning.data import CourseData, CourseEnrollmentData, UserData, UserPersonalData
from openedx_events.learning.signals import COURSE_ENROLLMENT_CHANGED

from openedx_plugin_sample.models import CourseArchiveStatus

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


def _build_enrollment(user, course_key, *, mode, is_active):
    """
    Build a CourseEnrollmentData payload like the platform would emit.
    """
    return CourseEnrollmentData(
        user=UserData(
            id=user.id,
            is_active=user.is_active,
            pii=UserPersonalData(username=user.username, email=user.email),
        ),
        course=CourseData(course_key=course_key, display_name="Demo Course"),
        mode=mode,
        is_active=is_active,
        creation_date=datetime.now(timezone.utc),
    )


@pytest.mark.django_db
def test_verified_upgrade_unarchives_course(user, course_key):
    """
    Test that firing COURSE_ENROLLMENT_CHANGED with is_active=True and
    mode="verified" flips an existing archived CourseArchiveStatus back to
    unarchived.
    """
    archive_status = CourseArchiveStatus.objects.create(
        course_id=course_key,
        user=user,
        is_archived=True,
        archive_date=datetime.now(timezone.utc),
    )

    COURSE_ENROLLMENT_CHANGED.send_event(
        enrollment=_build_enrollment(
            user, course_key, mode="verified", is_active=True
        )
    )

    archive_status.refresh_from_db()
    assert archive_status.is_archived is False
    assert archive_status.archive_date is None
