# Tutor Plugin Configuration Guide

This directory contains Tutor plugin configuration for easy deployment of both backend and frontend plugins in a Tutor-based Open edX deployment.

## Table of Contents

- [Overview](#overview)
- [Plugin Configuration](#plugin-configuration)
- [Installation Steps](#installation-steps)
- [Development vs Production](#development-vs-production)
- [Configuration Options](#configuration-options)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

## Overview

This Tutor plugin simplifies the deployment of the sample plugin by:

- **Backend Integration**: Automatically installs the Django app plugin
- **Frontend Integration**: Configures MFE slots for the custom components
- **Environment Setup**: Handles configuration across different deployment environments
- **Dependency Management**: Ensures all required packages are installed

**What is Tutor?**: Tutor is the official Docker-based deployment method for Open edX, providing simple commands for installation, configuration, and maintenance.

**Official Documentation:**
- [Tutor Documentation](https://docs.tutor.edly.io/)
- [Tutor Plugin Development](https://docs.tutor.edly.io/plugins/index.html)

## Plugin Configuration

**File**: [`sample_plugin.py`](./sample_plugin.py)

### Current Configuration

The current configuration demonstrates basic Tutor plugin structure:

```python
from tutormfe.hooks import PLUGIN_SLOTS

PLUGIN_SLOTS.add_items([
    # Replace the course_list
    (
        "learner-dashboard",
        "custom_course_list",
        """
        {
          op: PLUGIN_OPERATIONS.Insert,
          type: DIRECT_PLUGIN,
          priority: 50,
          RenderWidget: CourseList
        }"""
    ),
])
```

**Note**: The current implementation is a basic template. For full functionality, this needs to be expanded with proper backend installation and frontend package management.

### Complete Plugin Structure

A fully functional Tutor plugin should include:

```python
from tutor import hooks

# Plugin metadata
__version__ = "1.0.0"

# Backend plugin installation
@hooks.Filters.IMAGES_BUILD_MOUNTS.add()
def _mount_sample_plugin(mounts):
    """Mount the sample plugin source code for development."""
    mounts.append(("sample-plugin-backend", "/openedx/sample-plugin-backend"))
    return mounts

@hooks.Filters.LMS_ENV.add()
@hooks.Filters.CMS_ENV.add()
def _add_plugin_settings(env):
    """Add plugin-specific environment variables."""
    env["SAMPLE_PLUGIN_ENABLED"] = True
    return env

# Install backend plugin
@hooks.Filters.IMAGES_BUILD.add()
def _install_backend_plugin(build_config):
    """Install the backend plugin during image build."""
    build_config.add_dockerfile_commands(
        "RUN pip install -e /openedx/sample-plugin-backend"
    )
    return build_config

# Frontend plugin configuration  
from tutormfe.hooks import PLUGIN_SLOTS

PLUGIN_SLOTS.add_items([
    (
        "learner-dashboard",
        "course_list_slot", 
        """
        {
          op: PLUGIN_OPERATIONS.Replace,
          widget: {
            id: 'custom_course_list',
            type: DIRECT_PLUGIN,
            priority: 50,
            RenderWidget: CourseList
          }
        }"""
    ),
])
```

## Installation Steps

### Prerequisites

1. **Tutor Installation**: Follow [Tutor installation guide](https://docs.tutor.edly.io/install.html)
2. **Plugin Source**: Have the sample plugin source code available
3. **Tutor MFE Plugin**: Install tutor-mfe plugin if customizing frontend

### Step 1: Install Tutor Plugin

```bash
# Method 1: Install from local directory
pip install -e /path/to/sample-plugin/tutor/

# Method 2: Copy plugin file (simpler for development)
mkdir -p "$(tutor plugins printroot)"
cp sample_plugin.py "$(tutor plugins printroot)/sample_plugin.py"
```

### Step 2: Enable Plugin

```bash
# Enable the plugin
tutor plugins enable sample_plugin

# Verify plugin is enabled
tutor plugins list
```

### Step 3: Deploy Backend Plugin

```bash
# For development deployment
tutor dev launch

# For production deployment  
tutor local launch
```

### Step 4: Configure Frontend (if using MFE customization)

```bash
# If using tutor-mfe plugin for frontend customization
tutor plugins enable mfe
tutor local launch
```

### Step 5: Verify Installation

```bash
# Check backend plugin
tutor dev exec lms python manage.py shell -c "from sample_plugin.models import CourseArchiveStatus; print('Backend plugin loaded')"

# Check frontend plugin (visit learner dashboard in browser)
# Should see custom course list with archive functionality
```

## Development vs Production

### Development Mode

**Characteristics:**
- Uses `tutor dev` commands
- Mounts source code for live editing
- Faster iteration cycles
- Debug logging enabled

**Setup Pattern:**
```bash
# Mount backend plugin source
tutor dev mount /path/to/sample-plugin/backend:/openedx/sample-plugin-backend

# Start development environment
tutor dev launch

# Install plugin in development mode
tutor dev exec lms pip install -e ../sample-plugin-backend
tutor dev exec lms python manage.py migrate
tutor dev restart lms
```

### Production Mode

**Characteristics:**
- Uses `tutor local` commands
- Builds plugins into Docker images
- Optimized for performance
- Production logging levels

**Setup Pattern:**
```bash
# Enable plugin
tutor plugins enable sample_plugin

# Build and deploy
tutor local launch
```

### Key Differences

| Aspect | Development | Production |
|--------|-------------|------------|
| **Installation** | `pip install -e` (editable) | Built into image |
| **Code Changes** | Live reload | Requires rebuild |
| **Performance** | Slower (debug mode) | Optimized |
| **Database** | SQLite/development DB | Production database |
| **Logging** | Verbose | Production level |

## Configuration Options

### Backend Plugin Configuration

```python
# In tutor plugin
@hooks.Filters.LMS_ENV.add()
def _add_backend_settings(env):
    """Configure backend plugin settings."""
    env.update({
        # Plugin-specific settings
        "SAMPLE_PLUGIN_API_RATE_LIMIT": "100/minute",
        "SAMPLE_PLUGIN_ARCHIVE_RETENTION": "365",
        
        # Open edX Filters configuration
        "OPEN_EDX_FILTERS_CONFIG": {
            "org.openedx.learning.course.about.render.started.v1": {
                "pipeline": [
                    "sample_plugin.pipeline.ChangeCourseAboutPageUrl"
                ],
                "fail_silently": False,
            }
        }
    })
    return env
```

### Frontend Plugin Configuration

```python
# Configure MFE slots
PLUGIN_SLOTS.add_items([
    (
        "learner-dashboard",      # Target MFE
        "course_list_slot",       # Slot identifier  
        """
        {
          op: PLUGIN_OPERATIONS.Replace,  // Operation type
          widget: {
            id: 'custom_course_list',     // Unique widget ID
            type: DIRECT_PLUGIN,          // Plugin type
            priority: 50,                 // Load priority
            RenderWidget: CourseList      // Component reference
          }
        }"""
    ),
])
```

### Environment-Specific Configuration

```python
# Different settings for different environments
@hooks.Filters.LMS_ENV.add() 
def _configure_by_environment(env):
    """Apply environment-specific configuration."""
    if env.get("TUTOR_DEV", False):
        # Development settings
        env["SAMPLE_PLUGIN_DEBUG"] = True
        env["SAMPLE_PLUGIN_API_RATE_LIMIT"] = "1000/minute"
    else:
        # Production settings
        env["SAMPLE_PLUGIN_DEBUG"] = False
        env["SAMPLE_PLUGIN_API_RATE_LIMIT"] = "60/minute"
    
    return env
```

## Troubleshooting

### Common Issues

**Plugin Not Loading:**
```bash
# Check if plugin is enabled
tutor plugins list

# Check plugin syntax
python -m py_compile sample_plugin.py

# Verify plugin location
tutor plugins printroot
ls -la "$(tutor plugins printroot)/"
```

**Backend Plugin Not Installing:**
```bash
# Check build logs
tutor images build lms

# Manual installation for debugging
tutor dev exec lms pip install -e ../sample-plugin-backend
tutor dev exec lms python -c "import sample_plugin; print('Success')"

# Check migrations
tutor dev exec lms python manage.py showmigrations sample_plugin
```

**Frontend Plugin Not Appearing:**
```bash
# Check MFE configuration
tutor dev exec learner-dashboard env | grep PLUGIN

# Verify plugin slots
tutor dev logs learner-dashboard

# Check browser console for JavaScript errors
```

**Settings Not Applied:**
```bash
# Check environment variables
tutor dev exec lms env | grep SAMPLE_PLUGIN

# Verify Django settings
tutor dev exec lms python manage.py shell -c "from django.conf import settings; print(getattr(settings, 'SAMPLE_PLUGIN_DEBUG', 'Not set'))"
```

### Debug Commands

```bash
# View plugin configuration
tutor plugins show sample_plugin

# Check generated configuration
tutor config printvalue PLUGINS

# Inspect environment variables  
tutor dev exec lms env | grep -E "(SAMPLE_PLUGIN|OPEN_EDX)"

# Check plugin installation
tutor dev exec lms pip list | grep sample

# View logs
tutor dev logs lms
tutor dev logs learner-dashboard
```

### Getting Help

1. **Tutor Documentation**: [Plugin Development Guide](https://docs.tutor.edly.io/plugins/intro.html)
2. **Community**: [Tutor Community Forum](https://discuss.openedx.org/c/ops-and-deployment/tutor/)  
3. **GitHub**: [Tutor Repository Issues](https://github.com/overhangio/tutor/issues)

## Advanced Configuration

### Multi-MFE Plugin Configuration

```python
# Configure multiple MFEs
PLUGIN_SLOTS.add_items([
    # Learner Dashboard
    (
        "learner-dashboard",
        "course_list_slot",
        """{ /* CourseList configuration */ }"""
    ),
    
    # Course Authoring (if applicable)
    (
        "course-authoring", 
        "course_outline_slot",
        """{ /* Course outline customization */ }"""
    ),
])
```

### Custom Image Building

```python
@hooks.Filters.IMAGES_BUILD.add()
def _build_custom_image(build_config):
    """Build custom image with additional dependencies."""
    
    # Add system packages
    build_config.add_dockerfile_commands(
        "RUN apt-get update && apt-get install -y your-package"
    )
    
    # Install Python packages
    build_config.add_dockerfile_commands(
        "RUN pip install your-python-package"
    )
    
    # Copy additional files
    build_config.add_dockerfile_commands(
        "COPY custom-config.yml /openedx/config/"
    )
    
    return build_config
```

### Database Migrations

```python
@hooks.Actions.LMS_READY.add()
@hooks.Actions.CMS_READY.add() 
def _run_plugin_migrations():
    """Run plugin migrations when platform is ready."""
    from django.core.management import call_command
    call_command("migrate", "sample_plugin")
```

### Plugin Dependencies

```python
# In setup.py or pyproject.toml for your Tutor plugin
dependencies = [
    "tutor>=15.0.0",
    "tutor-mfe",  # If using MFE customization
]
```

### Environment Validation

```python
@hooks.Filters.CONFIG_UNIQUE.add()
def _validate_plugin_config(config):
    """Validate plugin configuration."""
    
    # Check required settings
    if not config.get("SAMPLE_PLUGIN_API_KEY"):
        raise ValueError("SAMPLE_PLUGIN_API_KEY is required")
    
    # Validate setting values
    rate_limit = config.get("SAMPLE_PLUGIN_API_RATE_LIMIT", "60/minute")
    if not re.match(r"^\d+/(minute|hour|day)$", rate_limit):
        raise ValueError(f"Invalid rate limit format: {rate_limit}")
    
    return config
```

This Tutor plugin configuration provides a foundation for deploying the sample plugin in production Open edX environments. The modular approach allows you to adapt the configuration for different deployment scenarios while maintaining consistency across environments.