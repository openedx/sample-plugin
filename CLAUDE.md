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
- `backend/` - Django app plugin with models, APIs, events, and filters
- `frontend/` - React component for MFE slot customization  
- `tutor/` - Tutor plugin for easy deployment
- Each directory has comprehensive README.md files with TOCs

**When Making Changes:**
- Prioritize educational value and clear examples over production optimization
- Always link to official Open edX documentation rather than duplicating it
- Maintain working integration between all plugin types
- Keep examples realistic but not overly complex

**Key Files and Their Relationships:**
- `backend/sample_plugin/apps.py` - Plugin registration and Django integration
- `backend/sample_plugin/signals.py` - Open edX Events handlers
- `backend/sample_plugin/pipeline.py` - Open edX Filters implementation
- `backend/sample_plugin/models.py` - CourseArchiveStatus model (business logic)
- `backend/sample_plugin/views.py` - REST API endpoints consumed by frontend
- `frontend/src/plugin.jsx` - React component that replaces course list slot
- `tutor/sample_plugin.py` - Deployment configuration (currently basic template)

## Build/Lint/Test Commands
- Make sure to set the following so that test output is not too verbose: `export PYTEST_ADDOPTS="--disable-warnings --no-header --tb=short"`
- Backend testing: `cd backend && pytest` or `cd backend && make test`
- Run a single test: `cd backend && pytest tests/test_models.py::test_placeholder`
- Quality checks: `cd backend && make quality`
- Install requirements: `cd backend && make requirements`
- Compile requirements: `cd backend && make compile-requirements`

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
- **Backend ↔ Frontend**: CourseArchiveStatus API in `views.py` consumed by `frontend/src/plugin.jsx`
- **Events ↔ Models**: Signal handlers in `signals.py` can update models in `models.py`
- **Settings ↔ Filters**: Filter registration in `settings/common.py` must match classes in `pipeline.py`
- **Apps.py ↔ All**: Plugin configuration affects URL routing, settings, and signal registration

### Open edX Plugin Patterns
- **API Development**: Use `perform_create()`/`perform_update()` in viewsets for business logic
- **Settings**: Use additive approach for `OPEN_EDX_FILTERS_CONFIG` to avoid plugin conflicts
- **Frontend**: Use Paragon components and `getAuthenticatedHttpClient()` for platform integration
- **Events**: Import signal handlers in `apps.py ready()` method for proper registration
- **Filters**: Return dictionaries with same parameter names as input, handle all scenarios
