"""
sample_plugin Django application initialization.
"""

from django.apps import AppConfig
from edx_django_utils.plugins.constants import PluginSettings, PluginURLs


class SamplePluginConfig(AppConfig):
    # pylint: disable=line-too-long
    """
    Configuration for the sample_plugin Django application as an edx-platform plugin

    See https://docs.openedx.org/projects/edx-django-utils/en/latest/plugins/how_tos/how_to_create_a_plugin_app.html#manual-setup
    for more details and examples.
    """  # noqa:

    default_auto_field = "django.db.models.BigAutoField"
    name = "sample_plugin"
    plugin_app = {
        "url_config": {
            "lms.djangoapp": {
                PluginURLs.NAMESPACE: "sample_plugin",
                PluginURLs.REGEX: r"^sample-plugin/",
                PluginURLs.RELATIVE_PATH: "urls",
            },
            "cms.djangoapp": {
                PluginURLs.NAMESPACE: "sample_plugin",
                PluginURLs.REGEX: r"^sample-plugin/",
                PluginURLs.RELATIVE_PATH: "urls",
            },
        },
        PluginSettings.CONFIG: {
            "lms.djangoapp": {
                "common": {
                    PluginURLs.RELATIVE_PATH: "settings.common",
                },
                "test": {
                    PluginURLs.RELATIVE_PATH: "settings.test",
                },
                "production": {
                    PluginURLs.RELATIVE_PATH: "settings.production",
                },
            },
            "cms.djangoapp": {
                "common": {
                    PluginURLs.RELATIVE_PATH: "settings.common",
                },
                "test": {
                    PluginURLs.RELATIVE_PATH: "settings.test",
                },
                "production": {
                    PluginURLs.RELATIVE_PATH: "settings.production",
                },
            },
        },
        # You could also define PluginSignals.CONFIG here as a part of this block
        # and define all our openedx-events connections here explicitly.  However,
        # it's much easier to just put all your signal recievers in one file and import
        # that file below as a par of the ready() function.
        #
        # Docs for using PluginSignals can be found here:
        #   https://docs.openedx.org/projects/edx-django-utils/en/latest/plugins/how_tos/how_to_create_a_plugin_app.html
    }

    def ready(self):
        """
        Do any app specific loading that needs to happen.
        """

        # Import the handlers file so that our signal recievers
        # get registered and can run when the relevant signals get
        # fired.
        from . import signals
