"""
Tutor plugin for the Open edX Sample Plugin.

Installs the backend Django app (openedx-sample-plugin from PyPI) into LMS/CMS
and configures the frontend MFE slot (from @openedx/sample-plugin on npm) in the
learner-dashboard.

Requirements:
    tutor>=17.0.0
    tutor-mfe (for frontend slot configuration)
"""

from tutor import hooks

try:
    from tutormfe.hooks import PLUGIN_SLOTS
    _tutormfe_available = True
except ImportError:
    _tutormfe_available = False

# ---------------------------------------------------------------------------
# Backend: Install the Django app plugin into LMS and CMS images
# ---------------------------------------------------------------------------
# The openedx-dockerfile-post-python-requirements patch runs after pip
# installs the base Open edX requirements. Plugins installed here are
# available in both LMS and CMS containers.
# ---------------------------------------------------------------------------

hooks.Filters.ENV_PATCHES.add_item((
    "openedx-dockerfile-post-python-requirements",
    "RUN pip install openedx-sample-plugin",
))

# ---------------------------------------------------------------------------
# Frontend: Install npm package and configure the learner-dashboard slot
# ---------------------------------------------------------------------------
# Only runs when tutor-mfe is installed, so the plugin degrades gracefully
# if someone uses this plugin without the MFE plugin.
# ---------------------------------------------------------------------------

if _tutormfe_available:
    # Step 1: Install the npm package into all MFE images.
    # Ideally this would use mfe-dockerfile-post-npm-install-learner-dashboard
    # to scope installation to only the MFE that needs it, but env.config.jsx
    # is a single shared file rendered for all MFEs. The buildtime import below
    # must resolve in every MFE's node_modules, so we install it globally.
    # The plugin slot config is still scoped to learner-dashboard at runtime.
    hooks.Filters.ENV_PATCHES.add_item((
        "mfe-dockerfile-post-npm-install",
        "RUN npm install @openedx/sample-plugin",
    ))

    # Step 2: Import the CourseList component in the MFE env config so it is
    # in scope when the plugin slot configuration is evaluated at runtime.
    # The mfe-env-config-buildtime-imports patch injects import statements
    # into the generated env.config.jsx file.
    hooks.Filters.ENV_PATCHES.add_item((
        "mfe-env-config-buildtime-imports",
        "import { CourseList } from '@openedx/sample-plugin';",
    ))

    # Step 3: Configure the course list plugin slot.
    # - Hide the default CourseList that ships with the learner-dashboard.
    # - Insert our custom CourseList that adds archive/unarchive functionality.
    #
    # Slot ID: org.openedx.frontend.learner_dashboard.course_list.v1
    # Props passed by the slot: courseListData (visibleList, numPages,
    #   setPageNumber, filterOptions, showFilters)
    PLUGIN_SLOTS.add_item((
        "learner-dashboard",
        "org.openedx.frontend.learner_dashboard.course_list.v1",
        """
        {
          op: PLUGIN_OPERATIONS.Hide,
          widgetId: 'default_contents',
        },
        {
          op: PLUGIN_OPERATIONS.Insert,
          widget: {
            id: 'sample_plugin_course_list',
            type: DIRECT_PLUGIN,
            priority: 50,
            RenderWidget: CourseList,
          },
        }""",
    ))
