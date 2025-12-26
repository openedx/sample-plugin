"""
A sample backend plugin for the Open edX Platform.
"""

from importlib.metadata import version as get_version

# The name of the package is `openedx-sample-plugin` but __package__ is `sample_plugin` so we hardcode the name of the
# package here so that the version fetching works correctly.  A lot of examples will show using `__package__`.
__version__ = get_version('openedx-sample-plugin')
