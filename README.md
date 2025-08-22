# Open edX Sample Plugin

A comprehensive example demonstrating all major plugin interfaces available in the Open edX platform. This repository shows how to extend Open edX functionality without modifying core platform code.

## Table of Contents

- [What This Repository Demonstrates](#what-this-repository-demonstrates)
- [Plugin Types & Official Documentation](#plugin-types--official-documentation)
- [Quick Start Guide](#quick-start-guide)
- [Learning Path for New Plugin Developers](#learning-path-for-new-plugin-developers)
- [Repository Structure](#repository-structure)
- [Development Workflows](#development-workflows)
- [Integration Examples](#integration-examples)
- [Troubleshooting](#troubleshooting)
- [Additional Resources](#additional-resources)

## What This Repository Demonstrates

This sample plugin showcases the **Open edX Hooks Extension Framework**, which allows you to extend the platform in a stable and maintainable way. The framework provides two main types of hooks:

- **Events**: React to things happening in the platform (e.g., when a course is published)
- **Filters**: Modify platform behavior (e.g., change where course about pages redirect)

**Key Concept**: All extensions are implemented as standard Django plugins that integrate seamlessly with edx-platform.

**Official Documentation**: [Hooks Extension Framework Overview](https://docs.openedx.org/en/latest/developers/concepts/hooks_extension_framework.html)

## Plugin Types & Official Documentation

| Plugin Type | What It Does | Official Documentation | Sample Code | When To Use |
|-------------|--------------|------------------------|-------------|-------------|
| **Django App Plugin** | Add models, APIs, views, and business logic | [How to create a plugin app](https://docs.openedx.org/projects/edx-django-utils/en/latest/plugins/how_tos/how_to_create_a_plugin_app.html) | [`backend/`](./backend/) | Adding new functionality, APIs, or data models |
| **Events (Signals)** | React to platform events | [Open edX Events Guide](https://docs.openedx.org/projects/openedx-events/en/latest/) | [`backend/sample_plugin/signals.py`](./backend/sample_plugin/signals.py) | Integrating with external systems, audit logging |
| **Filters** | Modify platform behavior | [Using Open edX Filters](https://docs.openedx.org/projects/openedx-filters/en/latest/how-tos/using-filters.html) | [`backend/sample_plugin/pipeline.py`](./backend/sample_plugin/pipeline.py) | Customizing business logic, URL redirects |
| **Frontend Slots** | Customize MFE interfaces | [Frontend Plugin Slots](https://docs.openedx.org/en/latest/site_ops/how-tos/use-frontend-plugin-slots.html) | [`frontend/`](./frontend/) | UI customization, adding new components |
| **Tutor Plugin** | Deploy plugins easily | [Tutor Plugin Development](https://docs.tutor.edly.io/) | [`tutor/`](./tutor/) | Simplified deployment and configuration |

## Quick Start Guide

### Prerequisites

1. **Platform Setup**: Follow the [Open edX Development Setup](https://docs.openedx.org/en/latest/developers/how-tos/get-ready-for-python-dev.html)
2. **Understanding**: Read the [Platform Overview](https://docs.openedx.org/en/latest/developers/concepts/platform_overview.html)

### Option 1: Development with Tutor (Recommended)

```bash
# Backend Plugin Setup
tutor mounts add lms:$PWD/backend:/openedx/sample-plugin-backend
tutor dev launch
tutor dev exec lms pip install -e ../sample-plugin-backend
tutor dev exec lms python manage.py lms migrate
tutor dev restart lms

# Frontend Plugin Setup (for learner-dashboard MFE development)
npm install $PWD/frontend
# Add env.config.jsx and module.config.js (see frontend/README.md)
npm start
```

### Option 2: Development without Tutor

```bash
# In your edx-platform directory
pip install -e /path/to/sample-plugin/backend

# Enable Learner Dashboard MFE
# Go to http://localhost:18000/admin/waffle/flag/
# Create flag: learner_home_mfe.enabled = Yes

# Run migrations
python manage.py lms migrate
```

### Verification

1. **Backend**: Visit `http://localhost:18000/sample-plugin/api/v1/course-archive-status/`
2. **Frontend**: Check learner dashboard for archive/unarchive functionality
3. **Events**: Check logs for course catalog change events
4. **Filters**: Course about page URLs should redirect to example.com

## Learning Path for New Plugin Developers

### 1. Understand the Architecture
- **Start here**: [Hooks Extension Framework](https://docs.openedx.org/en/latest/developers/concepts/hooks_extension_framework.html)
- **Deep dive**: [OEP-50: Hooks Extension Framework](https://docs.openedx.org/projects/openedx-proposals/en/latest/architectural-decisions/oep-0050-hooks-extension-framework.html)

### 2. Choose Your Plugin Type
Use the table above to identify which type of plugin matches your needs. You can combine multiple types in one plugin.

### 3. Study the Sample Code
- **Backend**: Start with [`backend/sample_plugin/apps.py`](./backend/sample_plugin/apps.py) to understand plugin registration
- **Events**: Examine [`backend/sample_plugin/signals.py`](./backend/sample_plugin/signals.py) for event handling patterns
- **Filters**: Review [`backend/sample_plugin/pipeline.py`](./backend/sample_plugin/pipeline.py) for behavior modification
- **Frontend**: Explore [`frontend/src/plugin.jsx`](./frontend/src/plugin.jsx) for UI customization

### 4. Run This Sample
Follow the [Quick Start Guide](#quick-start-guide) to see everything working together.

### 5. Adapt for Your Use Case
Each directory contains detailed README.md files with adaptation guidance.

## Repository Structure

```
sample-plugin/
├── README.md                           # This file - overview and quick start
├── backend/                           
│   ├── README.md                      # Backend plugin detailed guide
│   ├── sample_plugin/
│   │   ├── apps.py                    # Django plugin configuration
│   │   ├── models.py                  # Database models example
│   │   ├── views.py                   # REST API endpoints
│   │   ├── signals.py                 # Event handlers (Open edX Events)
│   │   ├── pipeline.py                # Filter implementations (Open edX Filters)
│   │   ├── settings/                  # Plugin settings configuration
│   │   └── urls.py                    # URL routing
│   └── tests/                         # Comprehensive test examples
├── frontend/
│   ├── README.md                      # Frontend plugin detailed guide
│   ├── src/
│   │   ├── plugin.jsx                 # React component for MFE slot
│   │   └── index.jsx                  # Export configuration
│   └── package.json                   # NPM package configuration
└── tutor/
    ├── README.md                      # Tutor deployment guide
    └── sample_plugin.py               # Tutor plugin configuration
```

## Development Workflows

### Backend Plugin Development

1. **Setup**: Follow backend setup in [Quick Start](#quick-start-guide)
2. **Development**: 
   - Modify models in `models.py`
   - Add API endpoints in `views.py`
   - Implement event handlers in `signals.py`
   - Create filters in `pipeline.py`
3. **Testing**: `cd backend && make test`
4. **Quality**: `cd backend && make quality`

**Detailed Guide**: See [`backend/README.md`](./backend/README.md)

### Frontend Plugin Development

1. **Setup**: Follow frontend setup in [Quick Start](#quick-start-guide)
2. **Development**:
   - Modify React components in `frontend/src/`
   - Test with local MFE development server
3. **Testing**: Integration testing with MFE

**Detailed Guide**: See [`frontend/README.md`](./frontend/README.md)

### Full-Stack Plugin Development

This sample shows how backend and frontend plugins work together:

- **Backend** provides API endpoints for course archive status
- **Frontend** consumes these APIs to show archive/unarchive UI
- **Events** log when course information changes
- **Filters** modify course about page URLs

## Integration Examples

### Backend + Frontend Integration

```python
# backend/sample_plugin/views.py - Provides API
class CourseArchiveStatusViewSet(viewsets.ModelViewSet):
    # API implementation
```

```jsx
// frontend/src/plugin.jsx - Consumes API
const response = await client.get(
  `${lmsBaseUrl}/sample-plugin/api/v1/course-archive-status/`
);
```

### Events + Filters Working Together

```python
# Events: Log course changes
@receiver(COURSE_CATALOG_INFO_CHANGED)
def log_course_info_changed(signal, sender, catalog_info, **kwargs):
    logging.info(f"{catalog_info.course_key} has been updated!")

# Filters: Modify course about URLs  
class ChangeCourseAboutPageUrl(PipelineStep):
    def run_filter(self, url, org, **kwargs):
        # Custom URL logic
```

## Troubleshooting

### Common Issues

**Plugin not loading:**
- Verify `setup.py` entry points are correct
- Check that plugin app is in INSTALLED_APPS (should be automatic)
- Review Django app plugin configuration in `apps.py`

**Events not firing:**
- Confirm signal receivers are imported in `apps.py` ready() method
- Check event is being sent by platform (some events only fire in specific contexts)
- Verify event data structure matches your handler signature

**Filters not working:**
- Ensure filter is registered in Django settings
- Check that filter step class inherits from `PipelineStep`
- Verify `run_filter` method returns correct dictionary format

**Frontend plugin not appearing:**
- Check MFE slot configuration in `env.config.jsx`
- Verify plugin is installed (`npm install`)
- Ensure slot exists in target MFE (check MFE documentation)

### Getting Help

1. **Documentation**: Start with official docs linked in the [Plugin Types table](#plugin-types--official-documentation)
2. **Community**: [Open edX Community Slack](https://openedx.org/slack)
3. **Forums**: [Open edX Discuss Forums](https://discuss.openedx.org)
4. **Issues**: Create issues in this repository for sample-specific problems

## Additional Resources

### Official Documentation
- **Platform**: [Open edX Developer Documentation](https://docs.openedx.org/en/latest/developers/)
- **Architecture**: [OEP-49: Django App Patterns](https://docs.openedx.org/projects/openedx-proposals/en/latest/best-practices/oep-0049-django-app-patterns.html)
- **Events**: [Open edX Events Reference](https://docs.openedx.org/projects/openedx-events/en/latest/reference/events.html)
- **Filters**: [Open edX Filters Reference](https://docs.openedx.org/projects/openedx-filters/en/latest/reference/filters.html)
- **Frontend**: [Available Frontend Plugin Slots](https://docs.openedx.org/en/latest/site_ops/references/frontend-plugin-slots.html)

### Community Resources
- **Cookiecutter**: [Django App Template](https://github.com/openedx/cookiecutter-django-app) for creating new plugins
- **Examples**: Other Open edX plugins in the [openedx organization](https://github.com/openedx)
- **Best Practices**: [OEP Index](https://docs.openedx.org/projects/openedx-proposals/en/latest/) for architectural guidance

### What This Sample Provides That Official Docs Don't
- **Working Integration**: Complete example showing all plugin types working together
- **Real Business Logic**: Realistic course archiving functionality vs. hello-world examples
- **Development Workflow**: End-to-end development and testing process
- **Troubleshooting**: Common plugin development issues and solutions