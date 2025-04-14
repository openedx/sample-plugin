"""
sample_plugin Django application initialization.
"""

from django.apps import AppConfig


class SamplePluginConfig(AppConfig):
    """
    Configuration for the sample_plugin Django application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sample_plugin'
