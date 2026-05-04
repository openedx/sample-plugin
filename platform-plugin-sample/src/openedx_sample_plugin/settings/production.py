"""
Production settings for the openedx_sample_plugin application.
"""

from openedx_sample_plugin.settings.common import plugin_settings as common_settings


def plugin_settings(settings):
    """
    Set up production-specific settings.

    Args:
        settings (dict): Django settings object
    """
    # Apply common settings
    common_settings(settings)
