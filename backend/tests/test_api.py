#!/usr/bin/env python
# pylint: disable=redefined-outer-name
"""
Tests for the `sample-plugin` REST API.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from opaque_keys.edx.keys import CourseKey
from rest_framework import status
from rest_framework.test import APIClient

from sample_plugin.models import CourseArchiveStatus

User = get_user_model()


@pytest.fixture
def api_client():
    """
    Return a REST framework API client.
    """
    return APIClient()


@pytest.fixture
def user():
    """
    Create and return a test user.
    """
    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="password123",
    )


@pytest.fixture
def another_user():
    """
    Create and return another test user.
    """
    return User.objects.create_user(
        username="anotheruser",
        email="anotheruser@example.com",
        password="password123",
    )


@pytest.fixture
def staff_user():
    """
    Create and return a test staff user.
    """
    return User.objects.create_user(
        username="staffuser",
        email="staffuser@example.com",
        password="password123",
        is_staff=True,
    )


@pytest.fixture
def course_key():
    """
    Create and return a test course key.
    """
    return CourseKey.from_string("course-v1:edX+DemoX+Demo_Course")


@pytest.fixture
def course_archive_status(user, course_key):
    """
    Create and return a test course archive status.
    """
    return CourseArchiveStatus.objects.create(
        course_id=course_key, user=user, is_archived=False
    )


@pytest.mark.django_db
def test_list_course_archive_status_authenticated(
    api_client, user, course_archive_status
):
    """
    Test that an authenticated user can list their own course archive statuses.
    """
    api_client.force_authenticate(user=user)
    url = reverse("sample_plugin:course-archive-status-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["course_id"] == str(
        course_archive_status.course_id
    )
    assert response.data["results"][0]["user"] == user.id
    assert (
        response.data["results"][0]["is_archived"] == course_archive_status.is_archived
    )


@pytest.mark.django_db
def test_list_course_archive_status_unauthenticated(api_client):
    """
    Test that an unauthenticated user cannot list course archive statuses.
    """
    url = reverse("sample_plugin:course-archive-status-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_course_archive_status_staff_can_see_all(
    api_client, staff_user, user, another_user, course_key
):
    """
    Test that a staff user can list all course archive statuses.
    """
    # Create archive statuses for both users
    CourseArchiveStatus.objects.create(
        course_id=course_key, user=user, is_archived=False
    )
    CourseArchiveStatus.objects.create(
        course_id=CourseKey.from_string("course-v1:edX+DemoX+Demo_Course2"),
        user=another_user,
        is_archived=True,
    )

    api_client.force_authenticate(user=staff_user)
    url = reverse("sample_plugin:course-archive-status-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 2


@pytest.mark.django_db
def test_create_course_archive_status(api_client, user, course_key):
    """
    Test that a user can create a course archive status.
    """
    api_client.force_authenticate(user=user)
    url = reverse("sample_plugin:course-archive-status-list")
    data = {
        "course_id": str(course_key),
        "user": user.id,
        "is_archived": True,
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["course_id"] == str(course_key)
    assert response.data["user"] == user.id
    assert response.data["is_archived"] is True
    assert response.data["archive_date"] is not None

    # Verify in database
    course_archive_status = CourseArchiveStatus.objects.get(
        course_id=course_key, user=user
    )
    assert course_archive_status.is_archived is True
    assert course_archive_status.archive_date is not None


@pytest.mark.django_db
def test_create_course_archive_status_for_another_user(
    api_client, user, another_user, course_key
):
    """
    Test that a regular user cannot create a course archive status for another user.
    """
    api_client.force_authenticate(user=user)
    url = reverse("sample_plugin:course-archive-status-list")
    data = {
        "course_id": str(course_key),
        "user": another_user.id,
        "is_archived": True,
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_staff_create_course_archive_status_for_another_user(
    api_client, staff_user, user, course_key
):
    """
    Test that a staff user can create a course archive status for another user.
    """
    api_client.force_authenticate(user=staff_user)
    url = reverse("sample_plugin:course-archive-status-list")
    data = {
        "course_id": str(course_key),
        "user": user.id,
        "is_archived": True,
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["course_id"] == str(course_key)
    assert response.data["user"] == user.id
    assert response.data["is_archived"] is True
    assert response.data["archive_date"] is not None


@pytest.mark.django_db
def test_update_course_archive_status(api_client, user, course_archive_status):
    """
    Test that a user can update their own course archive status.
    """
    api_client.force_authenticate(user=user)
    url = reverse(
        "sample_plugin:course-archive-status-detail", args=[course_archive_status.id]
    )
    data = {"is_archived": True}
    response = api_client.patch(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["is_archived"] is True
    assert response.data["archive_date"] is not None

    # Verify in database
    course_archive_status.refresh_from_db()
    assert course_archive_status.is_archived is True
    assert course_archive_status.archive_date is not None


@pytest.mark.django_db
def test_delete_course_archive_status(api_client, user, course_archive_status):
    """
    Test that a user can delete their own course archive status.
    """
    api_client.force_authenticate(user=user)
    url = reverse(
        "sample_plugin:course-archive-status-detail", args=[course_archive_status.id]
    )
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert CourseArchiveStatus.objects.filter(id=course_archive_status.id).count() == 0


@pytest.mark.django_db
def test_cannot_update_other_user_course_archive_status(
    api_client, another_user, course_archive_status
):
    """
    Test that a user cannot update another user's course archive status.
    """
    api_client.force_authenticate(user=another_user)
    url = reverse(
        "sample_plugin:course-archive-status-detail", args=[course_archive_status.id]
    )
    data = {"is_archived": True}
    response = api_client.patch(url, data, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_staff_can_update_other_user_course_archive_status(
    api_client, staff_user, course_archive_status
):
    """
    Test that a staff user can update another user's course archive status.
    """
    api_client.force_authenticate(user=staff_user)
    url = reverse(
        "sample_plugin:course-archive-status-detail", args=[course_archive_status.id]
    )
    data = {"is_archived": True}
    response = api_client.patch(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["is_archived"] is True


# New tests for optional user field behavior
@pytest.mark.django_db
def test_create_course_archive_status_without_user_field(api_client, user, course_key):
    """
    Test that a user can create a course archive status without specifying user field.
    The user field should default to the current user.
    """
    api_client.force_authenticate(user=user)
    url = reverse("sample_plugin:course-archive-status-list")
    data = {
        "course_id": str(course_key),
        "is_archived": True,
    }
    # Note: No "user" field in data
    response = api_client.post(url, data, format="json")

    if response.status_code != status.HTTP_201_CREATED:
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["course_id"] == str(course_key)
    assert response.data["user"] == user.id
    assert response.data["is_archived"] is True
    assert response.data["archive_date"] is not None

    # Verify in database
    course_archive_status = CourseArchiveStatus.objects.get(
        course_id=course_key, user=user
    )
    assert course_archive_status.is_archived is True
    assert course_archive_status.user == user


@pytest.mark.django_db
def test_update_course_archive_status_without_user_field(api_client, user, course_archive_status):
    """
    Test that a user can update their course archive status without specifying user field.
    The user field should remain unchanged.
    """
    api_client.force_authenticate(user=user)
    url = reverse(
        "sample_plugin:course-archive-status-detail", args=[course_archive_status.id]
    )
    data = {"is_archived": True}
    # Note: No "user" field in data
    response = api_client.patch(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["is_archived"] is True
    assert response.data["user"] == user.id
    assert response.data["archive_date"] is not None

    # Verify in database
    course_archive_status.refresh_from_db()
    assert course_archive_status.is_archived is True
    assert course_archive_status.user == user


@pytest.mark.django_db
def test_staff_create_with_explicit_user_override(
    api_client, staff_user, user, course_key
):
    """
    Test that staff can explicitly set user field to override default behavior.
    """
    api_client.force_authenticate(user=staff_user)
    url = reverse("sample_plugin:course-archive-status-list")
    data = {
        "course_id": str(course_key),
        "user": user.id,
        "is_archived": True,
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["course_id"] == str(course_key)
    assert response.data["user"] == user.id  # Should be the specified user, not staff_user
    assert response.data["is_archived"] is True

    # Verify in database
    course_archive_status = CourseArchiveStatus.objects.get(
        course_id=course_key, user=user
    )
    assert course_archive_status.user == user
    assert course_archive_status.user != staff_user


@pytest.mark.django_db
def test_staff_update_with_explicit_user_override(
    api_client, staff_user, user, another_user, course_key
):
    """
    Test that staff can explicitly change user field when updating.
    """
    # Create initial record for user
    initial_status = CourseArchiveStatus.objects.create(
        course_id=course_key, user=user, is_archived=False
    )

    api_client.force_authenticate(user=staff_user)
    url = reverse(
        "sample_plugin:course-archive-status-detail", args=[initial_status.id]
    )
    data = {
        "user": another_user.id,
        "is_archived": True,
    }
    response = api_client.patch(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["user"] == another_user.id  # Should be changed to another_user
    assert response.data["is_archived"] is True

    # Verify in database
    initial_status.refresh_from_db()
    assert initial_status.user == another_user
    assert initial_status.is_archived is True


@pytest.mark.django_db
def test_regular_user_cannot_override_user_field_create(
    api_client, user, another_user, course_key
):
    """
    Test that regular users cannot override user field to create records for other users.
    """
    api_client.force_authenticate(user=user)
    url = reverse("sample_plugin:course-archive-status-list")
    data = {
        "course_id": str(course_key),
        "user": another_user.id,  # Try to create for another user
        "is_archived": True,
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_staff_create_without_user_field_defaults_to_current_user(
    api_client, staff_user, course_key
):
    """
    Test that even staff users get records created for themselves when no user specified.
    """
    api_client.force_authenticate(user=staff_user)
    url = reverse("sample_plugin:course-archive-status-list")
    data = {
        "course_id": str(course_key),
        "is_archived": True,
    }
    # Note: No "user" field in data
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["course_id"] == str(course_key)
    assert response.data["user"] == staff_user.id  # Should default to current user (staff)
    assert response.data["is_archived"] is True

    # Verify in database
    course_archive_status = CourseArchiveStatus.objects.get(
        course_id=course_key, user=staff_user
    )
    assert course_archive_status.user == staff_user
