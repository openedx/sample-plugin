# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose and Context

This is a **sample plugin repository** that demonstrates all major Open edX plugin interfaces. It serves as a comprehensive example for developers new to Open edX plugin development.

**Key Context:**
- **Primary Goal**: Educational - show developers how to extend Open edX without modifying core platform code
- **Plugin Types Demonstrated**: Django App Plugin, Events (signals), Filters, Frontend Slots, Tutor Plugin
- **Real Business Logic**: Course archiving functionality (not just hello-world examples)
- **Target Audience**: Developers new to Open edX plugin development

**Repository Structure:**
- `backend-plugin-sample/` - Django app plugin with models, APIs, events, and filters
- `frontend-plugin-sample/` - React component plugged in via the legacy `frontend-plugin-framework` (FPF) and `env.config.jsx`
- `frontend-app-sample/` - frontend-base `App` (sibling of `frontend-plugin-sample/`) that registers slot operations on the bundled site
- `tutor-contrib-sample/` - Tutor plugin that installs one or the other depending on tutor-mfe's `FRONTEND_APPS` state
- Each directory has comprehensive README.md files with TOCs

**When Making Changes:**
- Prioritize educational value and clear examples over production optimization
- Always link to official Open edX documentation rather than duplicating it
- Maintain working integration between all plugin types
- Keep examples realistic but not overly complex

**Branch context:**
This branch ships *both* frontend stacks side by side: `frontend-plugin-sample/` (legacy FPF, identical to `main`) and `frontend-app-sample/` (frontend-base App). The Tutor plugin registers both unconditionally; each one self-no-ops when its target stack isn't in play. The FPF `PLUGIN_SLOTS` contribution only renders into the legacy learner-dashboard MFE (which tutor-mfe skips when the frontend-base learner-dashboard App is enabled), and the frontend-base App's slot operation targets a slot that only exists when the frontend-base learner-dashboard App is loaded. The operator picks the active path by flipping `apps["learner-dashboard"]["enabled"]` in tutor-mfe's `FRONTEND_APPS` filter. See [Port a Frontend Plugin from frontend-plugin-framework to frontend-base](https://docs.openedx.org/en/latest/site_ops/how-tos/port-frontend-plugin-to-frontend-base.html) for the conceptual differences between the two stacks.

**Key Files and Their Relationships:**
- `backend-plugin-sample/openedx_plugin_sample/apps.py` - Plugin registration and Django integration
- `backend-plugin-sample/openedx_plugin_sample/signals.py` - Open edX Events handlers
- `backend-plugin-sample/openedx_plugin_sample/pipeline.py` - Open edX Filters implementation
- `backend-plugin-sample/openedx_plugin_sample/models.py` - CourseArchiveStatus model (business logic)
- `backend-plugin-sample/openedx_plugin_sample/views.py` - REST API endpoints consumed by either frontend
- `frontend-plugin-sample/src/plugin.jsx` - Legacy FPF React component (imports from `@edx/frontend-platform`)
- `frontend-app-sample/src/CourseList.tsx` - frontend-base React component, TypeScript (imports from `@openedx/frontend-base`)
- `frontend-app-sample/src/app.tsx` - frontend-base `App` with slot operations targeting the learner-dashboard, TypeScript
- `tutor-contrib-sample/tutorsample/plugin.py` - Tutor plugin: backend pip install + unconditional registration of both frontend paths (FPF via `PLUGIN_SLOTS` and frontend-base via `FRONTEND_APPS` + site-config patches); each path self-no-ops when its target stack isn't active

## Build/Lint/Test Commands
- Make sure to set the following so that test output is not too verbose: `export PYTEST_ADDOPTS="--disable-warnings --no-header --tb=short"`
- Backend testing: `cd backend-plugin-sample && pytest` or `cd backend-plugin-sample && make test`
- Run a single test: `cd backend-plugin-sample && pytest tests/test_models.py::test_placeholder`
- Quality checks: `cd backend-plugin-sample && make quality`
- Install requirements: `cd backend-plugin-sample && make requirements`
- Compile requirements: `cd backend-plugin-sample && make compile-requirements`

## Code Style Guidelines
- Python: Follow PEP 8 with max line length of 120
- Use isort for import sorting
- Document classes and functions with docstrings
- Type hints are encouraged but not required
- Error handling should use appropriate exceptions with descriptive messages
- Use pytest for testing, with descriptive test function names
- Frontend uses React and follows standard JSX conventions

Always run `make quality` and fix issues before creating a PR to ensure consistent code style.

## Code Modification Guidelines

### Educational Constraints
- **Primary Goal**: Preserve teaching value - don't optimize away clarity for performance
- **Official Docs**: Always link to official Open edX documentation rather than duplicating explanations
- **Integration Focus**: Ensure all plugin types continue to work together as demonstration
- **Realistic Complexity**: Keep examples practical but not overly complex

### Code Relationships to Preserve
- **Backend ↔ Frontend**: CourseArchiveStatus API in `views.py` consumed by `frontend-plugin-sample/src/plugin.jsx`
- **Events ↔ Models**: Signal handlers in `signals.py` can update models in `models.py`
- **Settings ↔ Filters**: Filter registration in `settings/common.py` must match classes in `pipeline.py`
- **Apps.py ↔ All**: Plugin configuration affects URL routing, settings, and signal registration

### Open edX Plugin Patterns
- **API Development**: Use `perform_create()`/`perform_update()` in viewsets for business logic
- **Settings**: Use additive approach for `OPEN_EDX_FILTERS_CONFIG` to avoid plugin conflicts
- **Frontend**: Use Paragon components and import `getAuthenticatedHttpClient`/`getSiteConfig` from `@openedx/frontend-base` (not `@edx/frontend-platform`). The package's default export is the frontend-base `App`.
- **Events**: Import signal handlers in `apps.py ready()` method for proper registration
- **Filters**: Return dictionaries with same parameter names as input, handle all scenarios
