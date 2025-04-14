"""
Serializers for the sample_plugin app.
"""
from rest_framework import serializers

from sample_plugin.models import CourseArchiveStatus


class CourseArchiveStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for the CourseArchiveStatus model.
    """
    
    class Meta:
        """
        Meta class for CourseArchiveStatusSerializer.
        """
        model = CourseArchiveStatus
        fields = [
            'id',
            'course_id',
            'user',
            'is_archived',
            'archive_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'archive_date']