# tutor-contrib-sample

A Tutor plugin that installs and wires up the other sub-packages in this repo ([`backend-plugin-sample`](../backend-plugin-sample/), the two frontend siblings [`frontend-plugin-sample`](../frontend-plugin-sample/) and [`frontend-app-sample`](../frontend-app-sample/), and [`brand-sample`](../brand-sample/)) into a Tutor-based Open edX deployment. Enabling this plugin is the simplest way to see them working together.

## How to use it

See the root [README](../README.md) for the full setup. The minimum:

```bash
pip install -e ./tutor-contrib-sample
tutor plugins enable sample
tutor dev launch
```

[`tutor-mfe`](https://github.com/overhangio/tutor-mfe) is required for the frontend slot configuration to apply; the plugin degrades gracefully (backend + brand only) if it isn't installed.

## How it works

The plugin is a single file: [`tutorsample/plugin.py`](./tutorsample/plugin.py). Each section below is independent of the others.

**Backend.** Installs the published `openedx-plugin-sample` package from PyPI into the LMS and CMS images via the `openedx-dockerfile-post-python-requirements` patch. Also registers `backend-plugin-sample` as a `MOUNTED_DIRECTORIES` entry, so that running `tutor mounts add "$PWD/backend-plugin-sample"` bind-mounts your local checkout and pip-installs that instead.

**Migrations.** Adds `manage.py lms migrate openedx_plugin_sample` (and the CMS equivalent) to the `tutor … do init` task list.

**Frontend.** (Only when `tutor-mfe` is installed.) The plugin registers both frontend siblings unconditionally; each is inert unless its target stack is the active one, so the operator picks the path by flipping `apps["learner-dashboard"]["enabled"]` in tutor-mfe's `FRONTEND_APPS` filter.

- *frontend-plugin-framework* — installs the published `@openedx/plugin-sample` npm package into every MFE image, injects an `import { CourseList } from '@openedx/plugin-sample'` into the generated `env.config.jsx`, and wires `CourseList` into the `org.openedx.frontend.learner_dashboard.course_list.v1` slot (hiding the default contents). Renders into the legacy per-MFE learner-dashboard, which tutor-mfe skips when the frontend-base learner-dashboard App is enabled.
- *frontend-base* — registers `@openedx/frontend-app-sample` via the `FRONTEND_APPS` filter and adds it to the bundled site with `addApp()` through the `mfe-site-config-imports` / `mfe-site-config` patches. The App's own slot operation targets a slot that only exists when the frontend-base learner-dashboard App is loaded.

**Brand.** Sets `MFE_CONFIG["PARAGON_THEME_URLS"]` to load Paragon's default light theme overlaid with the compiled `brand-sample/dist/light.min.css` served from jsDelivr.

> TODO: the brand override currently assumes `brand-sample` has been pushed to jsDelivr from `main`. For a source-hacking workflow, this should be swapped for the [tutor-contrib-paragon](https://github.com/openedx/openedx-tutor-plugins/tree/main/plugins/tutor-contrib-paragon) flow described in [`brand-sample/README.md`](../brand-sample/README.md).
