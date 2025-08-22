"""
sample_plugin Django application initialization.
"""

from django.apps import AppConfig
from edx_django_utils.plugins.constants import PluginSettings, PluginURLs


class SamplePluginConfig(AppConfig):
    """
    Django App Plugin configuration for Open edX platform integration.

    This class demonstrates the complete Django App Plugin pattern, which allows
    you to add new functionality to edx-platform without modifying core code.

    Key Features Demonstrated:
    - URL configuration for both LMS and CMS
    - Settings integration across environments (common, test, production)
    - Signal handler registration for Open edX Events
    - Proper plugin app structure following Open edX patterns

    Official Documentation:
    - Plugin Creation: https://docs.openedx.org/projects/edx-django-utils/en/latest/plugins/how_tos/how_to_create_a_plugin_app.html
    - Plugin Overview: https://docs.openedx.org/projects/edx-django-utils/en/latest/plugins/readme.html
    - Hooks Framework: https://docs.openedx.org/en/latest/developers/concepts/hooks_extension_framework.html

    Real-World Usage:
    This pattern is used when you need to:
    - Add new models and database tables
    - Provide new REST API endpoints
    - Integrate with external systems via events
    - Modify platform behavior with filters
    - Add custom business logic

    Entry Point Configuration:
    This plugin is registered in setup.py as:
    ```python
    entry_points={
        "lms.djangoapp": ["sample_plugin = sample_plugin.apps:SamplePluginConfig"],
        "cms.djangoapp": ["sample_plugin = sample_plugin.apps:SamplePluginConfig"],
    }
    ```

    The platform automatically discovers and loads plugins registered in these entry points.
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
        # Alternative: PluginSignals.CONFIG
        # You can define signal connections here instead of in ready(), but the
        # ready() method approach is more flexible for complex signal handling.
        #
        # Example PluginSignals configuration:
        # PluginSignals.CONFIG: {
        #     "lms.djangoapp": {
        #         "relative_path": "signals",
        #         "receivers": [{
        #             "receiver_func_name": "log_course_info_changed",
        #             "signal_path": "openedx_events.content_authoring.signals.COURSE_CATALOG_INFO_CHANGED",
        #         }]
        #     }
        # }
        #
        # Documentation:
        # - PluginSignals: https://docs.openedx.org/projects/edx-django-utils/en/latest/plugins/how_tos/how_to_create_a_plugin_app.html#plugin-signals
        # - Open edX Events: https://docs.openedx.org/projects/openedx-events/en/latest/
    }

    def ready(self):
        """
        Initialize the plugin when Django starts.

        This method is called when Django initializes this app. It's the proper
        place to import signal handlers, register filters, and perform other
        startup tasks.

        Key Responsibilities:
        - Import signal handlers to register Open edX Event receivers
        - Register Open edX Filters (if not done via settings)
        - Initialize any plugin-specific configuration
        - Perform validation checks

        Django Documentation:
        - AppConfig.ready(): https://docs.djangoproject.com/en/stable/ref/applications/#django.apps.AppConfig.ready

        Open edX Documentation:
        - Events: https://docs.openedx.org/projects/openedx-events/en/latest/how-tos/consume-an-event.html
        - Filters: https://docs.openedx.org/projects/openedx-filters/en/latest/how-tos/using-filters.html

        Why Import in ready():
        Signal handlers must be imported for the @receiver decorators to register
        with Django's signal dispatcher. Importing in ready() ensures this happens
        when the app initializes, not when modules are first loaded.
        """
        # Import signal handlers to register Open edX Event receivers
        # This import registers all @receiver decorated functions in signals.py
        from . import signals  # noqa: F401
