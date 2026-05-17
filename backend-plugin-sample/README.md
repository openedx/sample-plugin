# backend-plugin-sample

A Django app plugin for edx-platform that adds a small course-archiving feature: learners can mark courses as archived (hidden from their active list) and unarchive them later. It demonstrates three backend extension points working together:

- A model + REST API (`CourseArchiveStatus`), consumed by [`frontend-plugin-sample`](../frontend-plugin-sample/)
- An [Open edX Events](https://docs.openedx.org/projects/openedx-events/en/latest/) handler that auto-unarchives on verified upgrade
- An [Open edX Filters](https://docs.openedx.org/projects/openedx-filters/en/latest/) pipeline step that rewrites the course-about URL

## How to use it

See the root [README](../README.md) for setup instructions. With Tutor, [`tutor-contrib-sample`](../tutor-contrib-sample/) installs this plugin automatically (or bind-mounts your local checkout if you `tutor mounts add` it). Without Tutor, `pip install -e .` into your edx-platform environment and run migrations.

## How it works

**Plugin registration.** [`apps.py`](./src/openedx_plugin_sample/apps.py) declares the Django app to edx-platform via the `plugin_app` config (URL routing, settings, signal registration). The entry points in [`pyproject.toml`](./pyproject.toml) make the platform discover the app automatically — no `INSTALLED_APPS` edit needed. See [How to create a plugin app](https://docs.openedx.org/projects/edx-django-utils/en/latest/plugins/how_tos/how_to_create_a_plugin_app.html).

**Model.** [`models.py`](./src/openedx_plugin_sample/models.py) defines `CourseArchiveStatus(user, course_id, is_archived, archive_date)`, indexed for the lookups the API performs. Registered in Django admin via [`admin.py`](./src/openedx_plugin_sample/admin.py).

**REST API.** [`views.py`](./src/openedx_plugin_sample/views.py) exposes the model as a DRF `ModelViewSet` at `/sample-plugin/api/v1/course-archive-status/`, with per-user permissions, throttling, and pagination. Serializer in [`serializers.py`](./src/openedx_plugin_sample/serializers.py); URLs in [`urls.py`](./src/openedx_plugin_sample/urls.py). Business logic (e.g. setting `archive_date` when `is_archived` flips true) lives in `perform_create`/`perform_update` rather than in the serializer.

**Event handler.** [`signals.py`](./src/openedx_plugin_sample/signals.py) listens for `COURSE_ENROLLMENT_CHANGED` and unarchives a learner's course when they upgrade to the verified track. An event (not a filter) is the right shape here because we want a one-time nudge at the moment of upgrade — if the learner re-archives the course later, we respect that. A filter would re-impose the rule on every render.

**Filter.** [`pipeline.py`](./src/openedx_plugin_sample/pipeline.py) implements `ChangeCourseAboutPageUrl`, a `PipelineStep` for `org.openedx.learning.course.about.render.started.v1` that rewrites course-about URLs to an external host. Registered via `OPEN_EDX_FILTERS_CONFIG` in [`settings/common.py`](./src/openedx_plugin_sample/settings/common.py).

**Settings.** Per-environment settings live in [`settings/`](./src/openedx_plugin_sample/settings/) (`common.py`, `production.py`, `test.py`). The plugin app loads these via its `plugin_app` config in `apps.py`.

## Testing and quality

```bash
cd backend-plugin-sample
make requirements   # install test deps
make test           # pytest
make quality        # lint
```

Tests live in [`tests/`](./tests/).
