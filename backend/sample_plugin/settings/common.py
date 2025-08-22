"""
Common settings for the sample_plugin application.

This module demonstrates how Django App Plugins integrate with the platform's
settings system. Plugin settings are merged with the main settings during
platform initialization.

Plugin Settings Integration:
The plugin_settings function is called during Django startup and receives
the main settings object. You can modify this object to add plugin-specific
configuration that integrates seamlessly with the platform.

Official Documentation:
- Plugin Settings: https://docs.openedx.org/projects/edx-django-utils/en/latest/plugins/how_tos/how_to_create_a_plugin_app.html#plugin-settings
- Django Settings: https://docs.djangoproject.com/en/stable/topics/settings/

Settings Organization:
- common.py: Settings for all environments
- production.py: Production-specific overrides  
- test.py: Test environment optimizations

Integration Points:
- OPEN_EDX_FILTERS_CONFIG: Register filters with the platform
- API rate limiting and throttling configuration
- Database connection settings for plugin models
- External service integration parameters
- Feature flags and environment-specific toggles
"""

import logging

logger = logging.getLogger(__name__)


def plugin_settings(settings):
    """
    Configure plugin-specific Django settings.

    This function is called during Django startup to merge plugin settings
    with the main platform configuration. All settings added here become
    available throughout the Django application.

    Args:
        settings (dict): Main Django settings object to modify

    Common Settings Patterns:

    # Plugin-specific configuration
    settings.SAMPLE_PLUGIN_API_RATE_LIMIT = "60/minute"
    settings.SAMPLE_PLUGIN_ARCHIVE_RETENTION_DAYS = 365
    
    # External service integration
    settings.SAMPLE_PLUGIN_EXTERNAL_API_URL = "https://api.example.com"
    settings.SAMPLE_PLUGIN_API_KEY = "your-api-key"
    
    # Feature flags
    settings.SAMPLE_PLUGIN_ENABLE_ARCHIVING = True
    settings.SAMPLE_PLUGIN_ENABLE_NOTIFICATIONS = False

    Environment-Specific Settings:
    Different environment files can override these settings:
    - production.py: Stricter rate limits, external API endpoints
    - test.py: Faster timeouts, mock services, in-memory databases
    - development.py: Debug logging, local service endpoints

    Security Considerations:
    - Never commit API keys or secrets to version control
    - Use environment variables for sensitive configuration
    - Validate setting values to prevent configuration errors
    """
    # Plugin is configured but no additional settings needed for this basic example
    # Uncomment and modify the examples below for your use case:
    
    # Plugin-specific configuration
    # settings.SAMPLE_PLUGIN_API_RATE_LIMIT = "60/minute"
    # settings.SAMPLE_PLUGIN_ARCHIVE_RETENTION_DAYS = 365
    
    # Register Open edX Filters (additive approach)
    _configure_openedx_filters(settings)


def _configure_openedx_filters(settings):
    """
    Configure Open edX Filters for the sample plugin.
    
    This function demonstrates the proper way to register filters by:
    1. Preserving existing filter configuration from other plugins
    2. Adding our filter configuration additively
    3. Avoiding duplicate pipeline steps
    4. Logging configuration state for debugging
    
    Args:
        settings (dict): Django settings object
    """
    # Get existing filter configuration (may be from other plugins or platform)
    filters_config = getattr(settings, 'OPEN_EDX_FILTERS_CONFIG', {})
    
    # Filter we want to register
    filter_name = "org.openedx.learning.course_about.page.url.requested.v1"
    our_pipeline_step = "sample_plugin.pipeline.ChangeCourseAboutPageUrl"
    
    # Check if this filter already has configuration
    if filter_name in filters_config:
        logger.debug(f"Filter {filter_name} already configured, adding our pipeline step")
        
        # Get existing pipeline steps
        existing_pipeline = filters_config[filter_name].get("pipeline", [])
        
        # Check if our pipeline step is already registered
        if our_pipeline_step in existing_pipeline:
            logger.info(
                f"Pipeline step {our_pipeline_step} already registered for filter {filter_name}. "
                "This may indicate the plugin is being loaded multiple times or another plugin "
                "has registered the same pipeline step."
            )
        else:
            # Add our pipeline step to existing configuration
            existing_pipeline.append(our_pipeline_step)
            filters_config[filter_name]["pipeline"] = existing_pipeline
            logger.debug(f"Added {our_pipeline_step} to existing filter configuration")
    else:
        # Create new filter configuration
        logger.debug(f"Creating new filter configuration for {filter_name}")
        filters_config[filter_name] = {
            "pipeline": [our_pipeline_step],
            "fail_silently": False,
        }
    
    # Update the settings object
    settings.OPEN_EDX_FILTERS_CONFIG = filters_config
    
    logger.debug(
        f"Final filter configuration for {filter_name}: "
        f"{filters_config.get(filter_name, {})}"
    )
