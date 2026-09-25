"""
Tutor plugin for the Open edX Sample Plugin.

Backend
-------
Installs the openedx-plugin-sample Django app into LMS/CMS, runs its
migrations, and (optionally) bind-mounts a local backend-plugin-sample
checkout into image builds.

Frontend
--------
Registers both frontend siblings:

* @openedx/plugin-sample is npm-installed into the legacy MFE images and
  contributes a PLUGIN_SLOTS entry that swaps in CourseList on the
  learner-dashboard's course list slot.

* @openedx/frontend-app-sample is registered as a frontend-base app and
  wired into the bundled site via the mfe-site-config-imports /
  mfe-site-config patches.

Requirements:
    tutor>=21.0.0
    tutor-mfe (for both legacy MFE slots and frontend-base site config)
"""
import json

from tutor import hooks

try:
    from tutormfe.hooks import FRONTEND_APPS, PLUGIN_SLOTS
    _tutormfe_available = True
except ImportError:
    _tutormfe_available = False

# ---------------------------------------------------------------------------
# Backend: Install the Django app plugin into LMS and CMS images
# ---------------------------------------------------------------------------

# The openedx-dockerfile-post-python-requirements patch runs after pip
# installs the base Open edX requirements. Plugins installed here are
# available in both LMS and CMS containers.

hooks.Filters.ENV_PATCHES.add_item((
    "openedx-dockerfile-post-python-requirements",
    "RUN pip install openedx-plugin-sample",
))

# Ensure that *if* backend-plugin-sample is bind-mounted, then it is mapped
# to /mnt/backend-plugin-sample and pip-installed as part of the openedx
# and openedx-dev image builds.

hooks.Filters.MOUNTED_DIRECTORIES.add_item(("openedx", "backend-plugin-sample"))

# ---------------------------------------------------------------------------
# Migrations: Run openedx_plugin_sample migrations on init
# ---------------------------------------------------------------------------

hooks.Filters.CLI_DO_INIT_TASKS.add_item((
    "lms",
    "./manage.py lms migrate openedx_plugin_sample",
))
hooks.Filters.CLI_DO_INIT_TASKS.add_item((
    "cms",
    "./manage.py cms migrate openedx_plugin_sample",
))

# ---------------------------------------------------------------------------
# Frontend: Register the frontend-base app and configure the legacy MFE slot
# ---------------------------------------------------------------------------
# Only runs when tutor-mfe is installed, so the plugin degrades gracefully
# if someone uses this plugin without the MFE plugin.
# ---------------------------------------------------------------------------

if _tutormfe_available:
    # ---- legacy FPF -----------------------------------------------------
    # Install the npm package into all MFE images.
    # Ideally this would use mfe-dockerfile-post-npm-install-learner-dashboard
    # to scope installation to only the MFE that needs it, but env.config.jsx
    # is a single shared file rendered for all MFEs. The buildtime import below
    # must resolve in every MFE's node_modules, so we install it globally.
    # The plugin slot config is still scoped to learner-dashboard at runtime.
    hooks.Filters.ENV_PATCHES.add_item((
        "mfe-dockerfile-post-npm-install",
        "RUN npm install @openedx/plugin-sample",
    ))

    # Import the CourseList component in the MFE env config so it is
    # in scope when the plugin slot configuration is evaluated at runtime.
    # The mfe-env-config-buildtime-imports patch injects import statements
    # into the generated env.config.jsx file.
    hooks.Filters.ENV_PATCHES.add_item((
        "mfe-env-config-buildtime-imports",
        "import { CourseList } from '@openedx/plugin-sample';",
    ))

    # Configure the course list plugin slot.
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
            id: 'openedx_plugin_sample_course_list',
            type: DIRECT_PLUGIN,
            priority: 50,
            RenderWidget: CourseList,
          },
        }""",
    ))

    # ---- frontend-base --------------------------------------------------
    # Register @openedx/frontend-app-sample with tutor-mfe so the site's
    # npm install picks it up. The FRONTEND_APPS filter is what tutor-mfe
    # iterates over when generating the site's package.json and site config.
    @FRONTEND_APPS.add()
    def _add_frontend_app_sample(apps):
        apps["sample"] = {
            "npm_package": "@openedx/frontend-app-sample",
            "npm_version": "*",
            "enabled": True,
        }
        return apps

    # Import the frontend-app-sample App in the generated site config so it
    # is in scope when addApp() is called. The mfe-site-config-imports patch
    # injects import statements into the generated site.config.*.tsx file.
    hooks.Filters.ENV_PATCHES.add_item((
        "mfe-site-config-imports",
        "import sampleApp from '@openedx/frontend-app-sample';",
    ))

    # Register the App on the bundled site via addApp(). The App's own
    # slot operations (defined in frontend-app-sample/src/app.tsx) target
    # the frontend-base learner-dashboard's course list slot; they are
    # inert if that App isn't enabled in the operator's FRONTEND_APPS.
    hooks.Filters.ENV_PATCHES.add_item((
        "mfe-site-config",
        "addApp(siteConfig, sampleApp);",
    ))

# ---------------------------------------------------------------------------
# Brand: Override Paragon theme CSS with brand-sample
# ---------------------------------------------------------------------------
# Open edX MFEs load their Paragon design-system CSS at runtime via the
# PARAGON_THEME_URLS setting. The "default" URL points at upstream Paragon;
# the optional "brandOverride" URL is loaded on top to recolor/restyle the
# theme. We point brandOverride at the compiled CSS in this repo's
# brand-sample/ directory, served via jsDelivr straight from GitHub.
#
# TODO: This assumes brand-sample has been pushed to jsdelivr.
#       Is it possible to set this up for dev so that it loads the brand from
#       the filesystem instead?
#       ANSWER: Yes, it is possible using the tutor-contrib-paragon plugin.
#       We should update this section to use that.
# ---------------------------------------------------------------------------

paragon_theme_urls = {
    "variants": {
        "light": {
            "urls": {
                "default": "https://cdn.jsdelivr.net/npm/@openedx/paragon@$paragonVersion/dist/light.min.css",
                "brandOverride": "https://cdn.jsdelivr.net/gh/openedx/sample-plugin@main/brand-sample/dist/light.min.css"
            }
        }
    }
}

brand_settings_lines = f"""
MFE_CONFIG["PARAGON_THEME_URLS"] = {json.dumps(paragon_theme_urls)}
"""

hooks.Filters.ENV_PATCHES.add_item(
    (
        "mfe-lms-common-settings",
        brand_settings_lines,
    )
)
