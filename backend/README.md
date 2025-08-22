# Backend Plugin Implementation Guide

This directory contains a comprehensive Django app plugin that demonstrates all major backend plugin interfaces available in Open edX. The plugin implements a course archiving system to show real-world usage patterns.

## Table of Contents

- [Overview](#overview)
- [Django App Plugin Configuration](#django-app-plugin-configuration)
- [Models & Database](#models--database)
- [API Endpoints](#api-endpoints)
- [Events & Signals](#events--signals)
- [Filters & Pipeline Steps](#filters--pipeline-steps)
- [Settings Configuration](#settings-configuration)
- [Development Setup](#development-setup)
- [Testing Your Plugin](#testing-your-plugin)
- [Integration Examples](#integration-examples)
- [Adapting This Plugin](#adapting-this-plugin)

## Overview

This backend plugin demonstrates the **Open edX Django App Plugin** pattern, which allows you to add new functionality to edx-platform without modifying core platform code.

**What this plugin provides:**
- **Models**: Course archive status tracking
- **APIs**: REST endpoints for frontend integration
- **Events**: React to course catalog changes
- **Filters**: Modify course about page URLs
- **Settings**: Plugin configuration management

**Official Documentation:**
- [Django App Plugins Overview](https://docs.openedx.org/projects/edx-django-utils/en/latest/plugins/readme.html)
- [How to create a plugin app](https://docs.openedx.org/projects/edx-django-utils/en/latest/plugins/how_tos/how_to_create_a_plugin_app.html)
- [Hooks Extension Framework](https://docs.openedx.org/en/latest/developers/concepts/hooks_extension_framework.html)

## Django App Plugin Configuration

**File**: [`sample_plugin/apps.py`](./sample_plugin/apps.py)

### Plugin Registration

The `SamplePluginConfig` class configures this app as an edx-platform plugin:

```python
class SamplePluginConfig(AppConfig):
    name = "sample_plugin"
    plugin_app = {
        "url_config": {
            # Register URLs for both LMS and CMS
            "lms.djangoapp": {
                PluginURLs.NAMESPACE: "sample_plugin",
                PluginURLs.REGEX: r"^sample-plugin/",
                PluginURLs.RELATIVE_PATH: "urls",
            },
            # ... CMS configuration
        },
        PluginSettings.CONFIG: {
            # Configure settings for different environments
            "lms.djangoapp": {
                "common": {PluginURLs.RELATIVE_PATH: "settings.common"},
                "production": {PluginURLs.RELATIVE_PATH: "settings.production"},
            },
            # ... CMS configuration  
        }
    }
```

### Key Configuration Options

| Option | Purpose | Official Docs |
|--------|---------|---------------|
| **url_config** | Register plugin URLs with platform | [Plugin URLs](https://docs.openedx.org/projects/edx-django-utils/en/latest/plugins/how_tos/how_to_create_a_plugin_app.html#plugin-urls) |
| **PluginSettings.CONFIG** | Load plugin settings | [Plugin Settings](https://docs.openedx.org/projects/edx-django-utils/en/latest/plugins/how_tos/how_to_create_a_plugin_app.html#plugin-settings) |
| **ready() method** | Initialize signal handlers | [Django AppConfig.ready()](https://docs.djangoproject.com/en/stable/ref/applications/#django.apps.AppConfig.ready) |

### Entry Points Configuration

In [`setup.py`](./setup.py), the plugin registers itself with edx-platform:

```python
entry_points={
    "lms.djangoapp": [
        "sample_plugin = sample_plugin.apps:SamplePluginConfig",
    ],
    "cms.djangoapp": [
        "sample_plugin = sample_plugin.apps:SamplePluginConfig", 
    ],
}
```

**Why this works**: The platform automatically discovers and loads any Django app registered in these entry points.

## Models & Database

**File**: [`sample_plugin/models.py`](./sample_plugin/models.py)  
**Official Docs**: [OEP-49: Django App Patterns](https://docs.openedx.org/projects/openedx-proposals/en/latest/best-practices/oep-0049-django-app-patterns.html)

### CourseArchiveStatus Model

```python
class CourseArchiveStatus(models.Model):
    course_id = CourseKeyField(max_length=255, db_index=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    is_archived = models.BooleanField(default=False, db_index=True)
    archive_date = models.DateTimeField(null=True, blank=True)
    # ... timestamps
```

**Key Features:**
- **CourseKeyField**: Uses Open edX's opaque keys for course identification
- **User Reference**: Links to platform's user model via `get_user_model()`
- **Database Indexes**: Performance optimization on frequently queried fields
- **Unique Constraints**: Prevents duplicate records per user-course combination

### Database Migration

```bash
# After modifying models.py
cd backend
python manage.py makemigrations sample_plugin
python manage.py migrate
```

**Migration files**: Generated in [`sample_plugin/migrations/`](./sample_plugin/migrations/)

### PII Annotations

The model includes PII documentation:
```python
# .. no_pii: This model does not store PII directly, only references to users via foreign keys.
```

**Best Practice**: Always document PII handling for Open edX compliance.

## API Endpoints

**File**: [`sample_plugin/views.py`](./sample_plugin/views.py)  
**URLs**: [`sample_plugin/urls.py`](./sample_plugin/urls.py)

### REST API Implementation

```python
class CourseArchiveStatusViewSet(viewsets.ModelViewSet):
    serializer_class = CourseArchiveStatusSerializer
    permission_classes = [IsOwnerOrStaffSuperuser]
    pagination_class = CourseArchiveStatusPagination
    throttle_classes = [CourseArchiveStatusThrottle]
    # ... filtering and ordering
```

### API Features

| Feature | Implementation | Why It Matters |
|---------|----------------|----------------|
| **Authentication** | `IsOwnerOrStaffSuperuser` permission | Users only see their own data; staff see all |
| **Pagination** | Custom pagination class | Performance with large datasets |
| **Throttling** | Rate limiting (60/minute) | Prevents API abuse |
| **Filtering** | DjangoFilterBackend | Query by course_id, user, archive status |
| **Validation** | Course ID format checking | Prevents injection attacks |

### API Endpoints

- **GET** `/sample-plugin/api/v1/course-archive-status/` - List archive statuses
- **POST** `/sample-plugin/api/v1/course-archive-status/` - Create new status
- **GET** `/sample-plugin/api/v1/course-archive-status/{id}/` - Get specific status
- **PUT/PATCH** `/sample-plugin/api/v1/course-archive-status/{id}/` - Update status
- **DELETE** `/sample-plugin/api/v1/course-archive-status/{id}/` - Delete status

### Business Logic

The viewset includes custom business logic:

```python
def perform_create(self, serializer):
    # Set archive_date when creating archived status
    data = {}
    if serializer.validated_data.get("is_archived", False):
        data["archive_date"] = timezone.now()
    instance = serializer.save(**data)
```

**Pattern**: Use `perform_create()` and `perform_update()` for business logic, following the pattern documented in [CLAUDE.md](../CLAUDE.md#api-development-guidelines).

## Events & Signals

**File**: [`sample_plugin/signals.py`](./sample_plugin/signals.py)  
**Official Docs**: [Open edX Events Guide](https://docs.openedx.org/projects/openedx-events/en/latest/)

### Event Handler Example

```python
from openedx_events.content_authoring.signals import COURSE_CATALOG_INFO_CHANGED
from django.dispatch import receiver

@receiver(COURSE_CATALOG_INFO_CHANGED)
def log_course_info_changed(signal, sender, catalog_info: CourseCatalogData, **kwargs):
    logging.info(f"{catalog_info.course_key} has been updated!")
    # Add your custom business logic here
```

### Available Events

**Event Catalog**: [Open edX Events Reference](https://docs.openedx.org/projects/openedx-events/en/latest/reference/events.html)

**Common Events:**
- `COURSE_CATALOG_INFO_CHANGED` - Course information updated
- `STUDENT_REGISTRATION_COMPLETED` - New user registered
- `CERTIFICATE_CREATED` - Certificate generated for learner
- `ENROLLMENT_CREATED` - Student enrolled in course

### Event Data Structure

Each event includes specific data. For `COURSE_CATALOG_INFO_CHANGED`:

```python
def log_course_info_changed(signal, sender, catalog_info: CourseCatalogData, **kwargs):
    # catalog_info contains:
    # - course_key: CourseKey object
    # - name: Course display name
    # - schedule: Course schedule information
    # - hidden: Visibility status
```

**Key Point**: Check the [event definition](https://docs.openedx.org/projects/openedx-events/en/latest/reference/events.html) to understand what data is available.

### Signal Handler Registration

Handlers are automatically registered via the `ready()` method in [`apps.py`](./sample_plugin/apps.py):

```python
def ready(self):
    # Import handlers to register signal receivers
    from . import signals
```

### Real-World Use Cases

- **Integration**: Send course updates to external systems
- **Analytics**: Track course lifecycle events
- **Notifications**: Email administrators about important changes
- **Auditing**: Log sensitive operations for compliance

## Filters & Pipeline Steps

**File**: [`sample_plugin/pipeline.py`](./sample_plugin/pipeline.py)  
**Official Docs**: [Using Open edX Filters](https://docs.openedx.org/projects/openedx-filters/en/latest/how-tos/using-filters.html)

### Filter Implementation

```python
from openedx_filters.filters import PipelineStep

class ChangeCourseAboutPageUrl(PipelineStep):
    def run_filter(self, url, org, **kwargs):
        # Extract course ID from URL
        pattern = r'(?P<course_id>course-v1:[^/]+)'
        match = re.search(pattern, url)
        
        if match:
            course_id = match.group('course_id')
            new_url = f"https://example.com/new_about_page/{course_id}"
            return {"url": new_url, "org": org}
        
        # Return original data if no match
        return {"url": url, "org": org}
```

### Filter Requirements

**Essential Elements:**
- Inherit from `PipelineStep`
- Implement `run_filter()` method
- Return dictionary with same parameter names as input
- Handle all possible input scenarios

### Available Filters

**Filter Catalog**: [Open edX Filters Reference](https://docs.openedx.org/projects/openedx-filters/en/latest/reference/filters.html)

**Common Filters:**
- Course enrollment filters
- Authentication filters  
- Certificate generation filters
- Course discovery filters

### Filter Registration

Filters must be registered in Django settings. This happens automatically via the plugin settings system (see [Settings Configuration](#settings-configuration)).

### Real-World Use Cases

- **URL Redirection**: Send users to custom course pages
- **Access Control**: Implement custom enrollment restrictions  
- **Data Transformation**: Modify course data before display
- **Integration**: Add custom fields to API responses

## Settings Configuration

**Files**: [`sample_plugin/settings/`](./sample_plugin/settings/)

### Settings Structure

```python
# settings/common.py
def plugin_settings(settings):
    """Add plugin settings to main settings object."""
    # Add your custom settings here
    # settings.SAMPLE_PLUGIN_API_KEY = "your-key"
    pass
```

### Environment-Specific Settings

- **`common.py`**: Settings for all environments
- **`production.py`**: Production-only settings
- **`test.py`**: Test-specific settings (faster database, etc.)

### Filter Registration via Settings

To register the URL filter, add to `common.py`:

```python
def plugin_settings(settings):
    # Register the course about page URL filter
    settings.OPEN_EDX_FILTERS_CONFIG = {
        "org.openedx.learning.course.about.render.started.v1": {
            "pipeline": [
                "sample_plugin.pipeline.ChangeCourseAboutPageUrl"
            ],
            "fail_silently": False,
        }
    }
```

**Filter Name Discovery**: Filter names are found in the [official filters documentation](https://docs.openedx.org/projects/openedx-filters/en/latest/reference/filters.html).

### Plugin-Specific Settings

Add custom configuration:

```python
def plugin_settings(settings):
    # Plugin-specific settings
    settings.SAMPLE_PLUGIN_ARCHIVE_RETENTION_DAYS = 365
    settings.SAMPLE_PLUGIN_API_RATE_LIMIT = "60/minute"
    settings.SAMPLE_PLUGIN_EXTERNAL_API_URL = "https://api.example.com"
```

## Development Setup

### Prerequisites

1. **Platform Setup**: [Open edX Development Guide](https://docs.openedx.org/en/latest/developers/how-tos/get-ready-for-python-dev.html)
2. **Python Environment**: Python 3.8+ with virtual environment

### Installation Methods

#### Option 1: With Tutor (Recommended)

```bash
# Mount the backend plugin
tutor mounts add lms:$PWD:/openedx/sample-plugin-backend

# Launch and install
tutor dev launch
tutor dev exec lms pip install -e ../sample-plugin-backend
tutor dev exec lms python manage.py lms migrate
tutor dev restart lms
```

#### Option 2: Direct Installation

```bash
# In your edx-platform directory
pip install -e /path/to/sample-plugin/backend

# Run migrations
python manage.py lms migrate
python manage.py cms migrate
```

### Verification Steps

1. **Check Installation**: 
   ```bash
   python manage.py lms shell
   >>> from sample_plugin.models import CourseArchiveStatus
   >>> print("Plugin installed successfully!")
   ```

2. **Test API**: Visit `http://localhost:18000/sample-plugin/api/v1/course-archive-status/`

3. **Check Admin**: Go to `http://localhost:18000/admin/` and look for "Course Archive Statuses"

## Testing Your Plugin

### Running Tests

```bash
cd backend

# Install test dependencies
make requirements

# Run all tests
make test

# Run specific test
pytest tests/test_models.py::test_course_archive_status_creation

# Run with coverage
make test-coverage
```

### Test Structure

**Test Files:**
- [`tests/test_models.py`](./tests/test_models.py) - Model functionality
- [`tests/test_api.py`](./tests/test_api.py) - API endpoint testing
- [`tests/test_plugin_integration.py`](./tests/test_plugin_integration.py) - Plugin integration

### Writing Plugin Tests

**Model Testing Pattern:**
```python
from django.test import TestCase
from sample_plugin.models import CourseArchiveStatus

class TestCourseArchiveStatus(TestCase):
    def test_create_archive_status(self):
        # Test model creation and validation
        pass
```

**API Testing Pattern:**
```python
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

class TestCourseArchiveStatusAPI(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="testuser")
        
    def test_list_archive_statuses(self):
        # Test API endpoints
        pass
```

### Quality Checks

```bash
# Run linting and quality checks
make quality

# Individual tools
pylint sample_plugin/
isort --check-only sample_plugin/
black --check sample_plugin/
```

## Integration Examples

### Backend + Frontend Integration

**API Endpoint** (`views.py`):
```python
class CourseArchiveStatusViewSet(viewsets.ModelViewSet):
    # Provides data for frontend consumption
```

**Frontend Consumption** (see [`../frontend/src/plugin.jsx`](../frontend/src/plugin.jsx)):
```javascript
const response = await client.get(
  `${lmsBaseUrl}/sample-plugin/api/v1/course-archive-status/`
);
```

### Events + API Integration

```python
@receiver(COURSE_CATALOG_INFO_CHANGED)
def sync_course_archive_on_change(signal, sender, catalog_info, **kwargs):
    # Update archive statuses when course info changes
    CourseArchiveStatus.objects.filter(
        course_id=catalog_info.course_key
    ).update(last_synced=timezone.now())
```

### Filters + Settings Integration

Settings configure filter behavior:
```python
# settings/common.py
def plugin_settings(settings):
    settings.SAMPLE_PLUGIN_REDIRECT_DOMAIN = "custom-domain.com"
    
# pipeline.py - Uses setting
class ChangeCourseAboutPageUrl(PipelineStep):
    def run_filter(self, url, org, **kwargs):
        redirect_domain = getattr(settings, 'SAMPLE_PLUGIN_REDIRECT_DOMAIN', 'example.com')
        new_url = f"https://{redirect_domain}/course/{course_id}"
        return {"url": new_url, "org": org}
```

## Adapting This Plugin

### For Your Use Case

1. **Models**: Modify [`models.py`](./sample_plugin/models.py) for your data structure
2. **APIs**: Update [`views.py`](./sample_plugin/views.py) and [`serializers.py`](./sample_plugin/serializers.py)  
3. **Events**: Change event handlers in [`signals.py`](./sample_plugin/signals.py)
4. **Filters**: Implement your business logic in [`pipeline.py`](./sample_plugin/pipeline.py)
5. **Settings**: Configure plugin behavior in [`settings/`](./sample_plugin/settings/)

### Plugin Development Checklist

- [ ] Update `setup.py` with your plugin name and dependencies
- [ ] Modify `apps.py` with your app configuration  
- [ ] Design your models in `models.py`
- [ ] Create and run database migrations
- [ ] Implement API endpoints in `views.py`
- [ ] Add event handlers in `signals.py`
- [ ] Create filters in `pipeline.py`
- [ ] Configure settings in `settings/`
- [ ] Write comprehensive tests
- [ ] Update documentation

### Common Customization Patterns

**Adding New Models:**
```python
class YourModel(models.Model):
    # Use Open edX field types when possible
    course_id = CourseKeyField(max_length=255)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    # ... your fields
```

**Adding New API Endpoints:**
```python
class YourViewSet(viewsets.ModelViewSet):
    # Follow the permission patterns from CourseArchiveStatusViewSet
    permission_classes = [IsOwnerOrStaffSuperuser]
    # ... your implementation
```

**Adding New Event Handlers:**
```python
@receiver(YOUR_CHOSEN_EVENT)
def handle_your_event(signal, sender, event_data, **kwargs):
    # Your business logic
    pass
```

This backend plugin provides a solid foundation for any Open edX extension. Focus on adapting the business logic while keeping the proven patterns for authentication, permissions, and integration.