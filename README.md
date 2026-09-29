# Open edX Sample Plugin

A worked example of every major Open edX plugin interface, built around a small "course archiving" feature you can run end-to-end. Use this repo as a reference when building your own Open edX plugin.

This is a monorepo of five sub-packages, each demonstrating one extension point:

| Sub-package | Plugin type | What it does |
|---|---|---|
| [`backend-plugin-sample/`](./backend-plugin-sample/) | [Django app plugin](https://docs.openedx.org/projects/edx-django-utils/en/latest/plugins/how_tos/how_to_create_a_plugin_app.html) | Adds a `CourseArchiveStatus` model with a REST API, an [Open edX Events](https://docs.openedx.org/projects/openedx-events/en/latest/) handler, and an [Open edX Filters](https://docs.openedx.org/projects/openedx-filters/en/latest/) pipeline step |
| [`frontend-plugin-sample/`](./frontend-plugin-sample/) | [MFE plugin slot widget](https://docs.openedx.org/en/latest/site_ops/how-tos/use-frontend-plugin-slots.html) ([frontend-plugin-framework](https://github.com/openedx/frontend-plugin-framework)) | Replaces the learner-dashboard course list with one that lets learners archive courses, on the legacy per-MFE build |
| [`frontend-app-sample/`](./frontend-app-sample/) | [frontend-base App](https://github.com/openedx/frontend-base) | The same course-list customization, ported to tutor-mfe's [frontend-base site](https://github.com/overhangio/tutor-mfe#frontend-base-site) |
| [`brand-sample/`](./brand-sample/) | [Paragon brand package](https://github.com/openedx/paragon) | An autumn-inspired color palette |
| [`tutor-contrib-sample/`](./tutor-contrib-sample/) | [Tutor plugin](https://docs.tutor.edly.io/) | Installs and wires up the others for a Tutor-based deployment |

> [!NOTE]
> There are two frontend siblings because the platform is mid-migration between frontend stacks. `frontend-plugin-sample/` targets the legacy frontend-plugin-framework, while `frontend-app-sample/` targets the newer frontend-base site. The Tutor plugin registers both; each self-no-ops when its target stack isn't active, and the operator picks the active path by flipping `apps["learner-dashboard"]["enabled"]` in tutor-mfe's `FRONTEND_APPS` filter. For the conceptual differences, see [Port a Frontend Plugin from frontend-plugin-framework to frontend-base](https://docs.openedx.org/en/latest/site_ops/how-tos/port-frontend-plugin-to-frontend-base.html).

## Development with Tutor

Requires [Tutor](https://docs.tutor.edly.io/install.html) >= 20 with [tutor-mfe](https://github.com/overhangio/tutor-mfe), and an Open edX environment that supports design tokens (Paragon >= 23, "Teak" release or later).

### Running the demo as-is

The `tutor-contrib-sample` plugin in this repo installs the published backend, frontend, and brand packages and wires them into Tutor:

```bash
pip install -e ./tutor-contrib-sample
tutor plugins enable sample
tutor dev launch
```

This is enough to see everything working: visit the learner dashboard and you should see the customized course list rendered with the brand applied. See [`tutor-contrib-sample/README.md`](./tutor-contrib-sample/README.md) for what each piece of the plugin does.

### Hacking on the source

To edit code in this repo and have your changes apply inside Tutor:

- **Backend** — `tutor-contrib-sample` registers `backend-plugin-sample` as a mounted directory, so a single command before launch is enough:

  ```bash
  tutor mounts add "$PWD/backend-plugin-sample"
  tutor dev launch
  ```

- **Frontend (frontend-plugin-framework)** — bind-mount a local MFE checkout into `tutor-mfe`, then point its webpack at your local `frontend-plugin-sample` checkout. See [`frontend-plugin-sample/README.md`](./frontend-plugin-sample/README.md).

- **Frontend (frontend-base)** — set up a frontend-base site with `frontend-app-sample` in its `packages/`, then run `npm run dev:packages`. See [`frontend-app-sample/README.md`](./frontend-app-sample/README.md).

- **Brand** — use [tutor-contrib-paragon](https://github.com/openedx/openedx-tutor-plugins/tree/main/plugins/tutor-contrib-paragon) to recompile and serve the brand from disk. See [`brand-sample/README.md`](./brand-sample/README.md).

## Development without Tutor

This path assumes you already have edx-platform running locally (bare-metal or devstack-style venv) and at least one MFE checked out.

- **Backend** — install editable into the edx-platform Python environment and migrate:

  ```bash
  pip install -e ./backend-plugin-sample
  python manage.py lms migrate openedx_plugin_sample
  python manage.py cms migrate openedx_plugin_sample
  ```

- **Frontend (frontend-plugin-framework)** — in your MFE checkout, add the `module.config.js` and `env.config.jsx` shown in [`frontend-plugin-sample/README.md`](./frontend-plugin-sample/README.md), then `npm ci && npm start`.

- **Frontend (frontend-base)** — add `frontend-app-sample` to your frontend-base site's `packages/` and register its App in the site config, then run `npm run dev:packages`. See [`frontend-app-sample/README.md`](./frontend-app-sample/README.md).

- **Brand** — set `PARAGON_THEME_URLS.variants.light.urls.brandOverride` in your MFE's `env.config.js[x]` (or `theme.variants.light.url` in a frontend-base `site.config.tsx`) to `https://cdn.jsdelivr.net/gh/openedx/sample-plugin@main/brand-sample/dist/light.min.css`. See [`brand-sample/README.md`](./brand-sample/README.md) for the full snippet.

  > TODO: a fully local brand-development flow without Tutor (recompile + serve from disk) is not yet documented.

## Getting help

- Open edX [community Slack](https://openedx.org/slack) and [discussion forums](https://discuss.openedx.org)
- Issues with this sample specifically: [openedx/sample-plugin issues](https://github.com/openedx/sample-plugin/issues)
