# tutor-contrib-sample

A Tutor plugin that installs and wires up the three other sub-packages in this repo ([`backend-plugin-sample`](../backend-plugin-sample/), [`frontend-plugin-sample`](../frontend-plugin-sample/), and [`brand-sample`](../brand-sample/)) into a Tutor-based Open edX deployment. Enabling this plugin is the simplest way to see all three working together.

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

**Frontend.** (Only when `tutor-mfe` is installed.) Installs the published `@openedx/plugin-sample` npm package into every MFE image, injects an `import { CourseList } from '@openedx/plugin-sample'` into the generated `env.config.jsx`, and wires `CourseList` into the `org.openedx.frontend.learner_dashboard.course_list.v1` slot (hiding the default contents).

**Brand.** Sets `MFE_CONFIG["PARAGON_THEME_URLS"]` to load Paragon's default light theme overlaid with the compiled `brand-sample/dist/light.min.css` served from jsDelivr.

> TODO: the brand override currently assumes `brand-sample` has been pushed to jsDelivr from `main`. For a source-hacking workflow, this should be swapped for the [tutor-contrib-paragon](https://github.com/openedx/openedx-tutor-plugins/tree/main/plugins/tutor-contrib-paragon) flow described in [`brand-sample/README.md`](../brand-sample/README.md).
