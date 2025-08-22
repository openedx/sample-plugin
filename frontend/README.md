# Frontend Plugin Implementation Guide

This directory contains a React component that demonstrates how to customize Open edX micro-frontends (MFEs) using the Frontend Plugin Framework. The plugin replaces the default course list in the learner dashboard with a custom implementation that includes course archiving functionality.

## Table of Contents

- [Overview](#overview)
- [Frontend Plugin Framework](#frontend-plugin-framework)
- [CourseList Component Example](#courselist-component-example)
- [Slot Integration Patterns](#slot-integration-patterns)
- [API Integration](#api-integration)
- [Development Workflow](#development-workflow)
- [Deployment Considerations](#deployment-considerations)
- [Customizing This Example](#customizing-this-example)
- [Troubleshooting](#troubleshooting)

## Overview

This frontend plugin demonstrates **Open edX MFE customization** using the Frontend Plugin Framework to replace the course list component in the learner dashboard.

**What this plugin provides:**
- **Custom CourseList Component**: Enhanced course display with archive functionality
- **Backend API Integration**: Connects to the sample backend plugin APIs
- **Slot Replacement Pattern**: Shows how to replace existing MFE components
- **State Management**: React patterns for plugin development
- **Authentication Integration**: Uses Open edX authentication system

**Official Documentation:**
- [Frontend Plugin Slots](https://docs.openedx.org/en/latest/site_ops/how-tos/use-frontend-plugin-slots.html)
- [Available Plugin Slots Reference](https://docs.openedx.org/en/latest/site_ops/references/frontend-plugin-slots.html)
- [OEP-65: Frontend Composability](https://docs.openedx.org/projects/openedx-proposals/en/latest/architectural-decisions/oep-0065-arch-frontend-composability.html)

## Frontend Plugin Framework

### What Are Plugin Slots?

A "frontend plugin slot" is an area of a web page that can be customized with different visual elements without forking the codebase. This allows site operators to customize MFEs using configuration files.

**Key Concepts:**
- **Slot**: A predefined customization point in an MFE
- **Plugin**: Custom code that fills or modifies a slot
- **Operations**: Actions you can take on slots (Insert, Modify, Replace)

### Plugin Operations

| Operation | What It Does | When To Use |
|-----------|--------------|-------------|
| **Insert** | Add new components before/after existing ones | Adding new features alongside existing ones |
| **Modify** | Change properties of existing components | Tweaking existing functionality |
| **Replace** | Completely replace existing components | Major customization (like this example) |

### Discovering Available Slots

**Slot Documentation**: [Available Frontend Plugin Slots](https://docs.openedx.org/en/latest/site_ops/references/frontend-plugin-slots.html)

**MFE-Specific Slots**: Each MFE documents its slots in `/src/plugin-slots/` directory:
- [Learner Dashboard Slots](https://github.com/openedx/frontend-app-learner-dashboard/tree/master/src/plugin-slots)
- [Course Authoring Slots](https://github.com/openedx/frontend-app-course-authoring/tree/master/src/plugin-slots)
- [Gradebook Slots](https://github.com/openedx/frontend-app-gradebook/tree/master/src/plugin-slots)

## CourseList Component Example

**File**: [`src/plugin.jsx`](./src/plugin.jsx)

### Component Structure

```jsx
const CourseList = ({ courseListData }) => {
  const [archivedCourses, setArchivedCourses] = useState(new Set());
  const [loadingStates, setLoadingStates] = useState(new Map());

  // Component implementation...
};
```

### Key Features

#### 1. Slot Data Integration

The component receives `courseListData` from the learner dashboard slot:

```jsx
// Safety check for slot data
if (!courseListData || !courseListData.visibleList) {
  return <div>Loading courses...</div>;
}

const courses = courseListData.visibleList;
```

**Slot Props**: Each slot provides specific data. For CourseListSlot, see the [slot documentation](https://github.com/openedx/frontend-app-learner-dashboard/tree/master/src/plugin-slots/CourseListSlot#plugin-props).

#### 2. Backend API Integration

```jsx
useEffect(() => {
  const fetchArchivedCourses = async () => {
    const client = getAuthenticatedHttpClient();
    const lmsBaseUrl = getConfig().LMS_BASE_URL;
    
    const response = await client.get(
      `${lmsBaseUrl}/sample-plugin/api/v1/course-archive-status/`,
      { params: { is_archived: true } }
    );
    
    const archivedCourseIds = new Set(
      response.data.results.map((item) => item.course_id)
    );
    setArchivedCourses(archivedCourseIds);
  };

  fetchArchivedCourses();
}, []);
```

**Key Patterns:**
- **Authentication**: `getAuthenticatedHttpClient()` handles Open edX auth
- **Configuration**: `getConfig().LMS_BASE_URL` gets platform URLs
- **Error Handling**: Try/catch blocks for API failures

#### 3. Open edX UI Components

The plugin uses **Paragon** (Open edX's design system):

```jsx
import {
  Card,
  Container,
  Row,
  Col,
  Badge,
  Collapsible,
  Button,
  Spinner,
  Dropdown,
  IconButton,
  Icon,
} from "@openedx/paragon";
import { Archive, Unarchive, MoreVert } from "@openedx/paragon/icons";
```

**Why Paragon**: Ensures consistent styling with the rest of Open edX interfaces.

**Paragon Documentation**: [Paragon Design System](https://paragon-openedx.netlify.app/)

### State Management

#### Archive Status Management

```jsx
const [archivedCourses, setArchivedCourses] = useState(new Set());
const [loadingStates, setLoadingStates] = useState(new Map());

const handleArchiveToggle = async (courseId, isCurrentlyArchived) => {
  setLoadingStates((prev) => new Map(prev).set(courseId, true));
  
  try {
    // API calls to backend
    if (isCurrentlyArchived) {
      // Unarchive logic
    } else {
      // Archive logic
    }
    
    // Update local state
    setArchivedCourses((prev) => {
      const newSet = new Set(prev);
      isCurrentlyArchived ? newSet.delete(courseId) : newSet.add(courseId);
      return newSet;
    });
  } catch (error) {
    console.error("Archive operation failed:", error);
  } finally {
    setLoadingStates((prev) => {
      const newMap = new Map(prev);
      newMap.delete(courseId);
      return newMap;
    });
  }
};
```

**Patterns Used:**
- **Optimistic Updates**: Update UI immediately, rollback on failure
- **Loading States**: Track loading per course for better UX
- **Immutable Updates**: Use functional setState for complex state

## Slot Integration Patterns

### CourseListSlot Integration

**Target Slot**: `course_list_slot` in learner dashboard

**Configuration Pattern** (for local development in `env.config.jsx`):

```javascript
import { DIRECT_PLUGIN, PLUGIN_OPERATIONS } from '@openedx/frontend-plugin-framework';
import { CourseList } from '@feanil/sample-plugin';

const config = {
  pluginSlots: {
    course_list_slot: {
      keepDefault: false,  // Hide original component
      plugins: [
        {
          op: PLUGIN_OPERATIONS.Insert,
          widget: {
            id: 'custom_course_list',
            type: DIRECT_PLUGIN,
            priority: 60,
            RenderWidget: CourseList  // Your custom component
          },
        },
      ],
    },
  },
}
```

### Plugin Configuration Options

| Option | Purpose | Values |
|--------|---------|--------|
| **keepDefault** | Show/hide original component | `true`, `false` |
| **op** | Plugin operation type | `Insert`, `Modify`, `Replace` |
| **priority** | Loading order | Higher numbers load later |
| **type** | Plugin implementation type | `DIRECT_PLUGIN`, `IFRAME_PLUGIN` |
| **RenderWidget** | Your React component | Component reference |

### Slot Props and Data

Each slot provides specific props. For CourseListSlot:

```jsx
const CourseList = ({ 
  courseListData,  // Course data from platform
  // Other props depend on the slot
}) => {
  // courseListData.visibleList - Array of course objects
  // courseListData.course - Course metadata
  // courseListData.courseRun - Course run information
};
```

**Finding Slot Props**: Check the slot's README in the MFE repository, or examine the slot implementation in `/src/plugin-slots/`.

## API Integration

### Authentication Patterns

**Open edX Authentication**:
```jsx
import { getAuthenticatedHttpClient } from "@edx/frontend-platform/auth";

const client = getAuthenticatedHttpClient();
// Client automatically includes authentication headers
```

**Configuration Access**:
```jsx
import { getConfig } from "@edx/frontend-platform";

const lmsBaseUrl = getConfig().LMS_BASE_URL;
const apiUrl = `${lmsBaseUrl}/sample-plugin/api/v1/course-archive-status/`;
```

### Error Handling Best Practices

```jsx
try {
  const response = await client.post(url, data);
  // Success handling
} catch (error) {
  console.error("API Error:", {
    status: error.response?.status,
    statusText: error.response?.statusText,
    data: error.response?.data,
    message: error.message,
  });
  
  // User feedback
  // Consider using toast notifications or error states
}
```

### API Response Handling

```jsx
// Handle paginated responses
const response = await client.get(url);
const items = response.data.results || [];  // DRF pagination format

// Handle different response formats
if (response.data && Array.isArray(response.data)) {
  // Direct array response
} else if (response.data.results) {
  // Paginated response
} else {
  // Single object response
}
```

## Development Workflow

### Prerequisites

1. **MFE Setup**: Have a learner dashboard MFE running locally
2. **Backend Plugin**: Install the backend plugin (see [`../backend/README.md`](../backend/README.md))
3. **Node.js**: Version 16+ with npm or yarn

### Local Development Setup

#### Step 1: Install Plugin Package

```bash
# In your MFE directory (e.g., frontend-app-learner-dashboard)
npm install /path/to/sample-plugin/frontend
```

#### Step 2: Create env.config.jsx

Create `env.config.jsx` in your MFE root (not committed to repo):

```javascript
import { DIRECT_PLUGIN, PLUGIN_OPERATIONS } from '@openedx/frontend-plugin-framework';
import { CourseList } from '@feanil/sample-plugin';

const config = {
  pluginSlots: {
    course_list_slot: {
      keepDefault: false,
      plugins: [
        {
          op: PLUGIN_OPERATIONS.Insert,
          widget: {
            id: 'custom_course_list',
            type: DIRECT_PLUGIN,
            priority: 60,
            RenderWidget: CourseList
          },
        },
      ],
    },
  },
}

export default config;
```

#### Step 3: Create module.config.js

Create `module.config.js` for local development:

```javascript
module.exports = {
  localModules: [
    {
      moduleName: '@feanil/sample-plugin', 
      dir: '/path/to/sample-plugin/frontend'
    },
  ],
};
```

**Purpose**: Webpack uses your local plugin code instead of the installed package.

#### Step 4: Start Development

```bash
# In your MFE directory
npm ci
npm start
```

### Development vs Production Configuration

**Local Development**:
- Uses `env.config.jsx` for slot configuration
- Uses `module.config.js` for local code loading
- Hot reload for faster development

**Production Deployment**:
- Configuration via Tutor plugins
- Plugin installed as npm package
- Optimized builds and caching

### Testing Frontend Plugins

#### Unit Testing

```javascript
// Example test structure
import { render, screen } from '@testing-library/react';
import { CourseList } from './plugin';

describe('CourseList Plugin', () => {
  test('renders course list with archive functionality', () => {
    const mockCourseData = {
      visibleList: [/* mock course data */]
    };
    
    render(<CourseList courseListData={mockCourseData} />);
    
    expect(screen.getByText('Archive')).toBeInTheDocument();
  });
});
```

#### Integration Testing

Test within the actual MFE environment:

1. Set up MFE with plugin installed
2. Create test courses in platform
3. Verify plugin functionality
4. Test API integration
5. Check error handling

## Deployment Considerations

### Production Deployment with Tutor

**Tutor Plugin Configuration** (see [`../tutor/README.md`](../tutor/README.md)):

```python
# In tutor plugin
PLUGIN_SLOTS.add_items([
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

### Performance Considerations

**Bundle Size**:
- Frontend plugins are included in MFE bundles
- Minimize dependencies and use tree shaking
- Consider lazy loading for large plugins

**API Performance**:
- Implement proper caching strategies
- Use pagination for large datasets  
- Optimize backend API response times

**User Experience**:
- Show loading states during API calls
- Handle errors gracefully
- Provide offline fallback behavior

### Browser Compatibility

- Follow MFE browser support requirements
- Test across different browsers
- Use polyfills if needed for newer JS features

## Customizing This Example

### For Different Slots

1. **Identify Target Slot**: Check [available slots](https://docs.openedx.org/en/latest/site_ops/references/frontend-plugin-slots.html)
2. **Study Slot Props**: Examine slot documentation for available data
3. **Adapt Component**: Modify component to work with slot-specific data
4. **Update Configuration**: Change slot name in plugin configuration

**Example - Adapting for Header Slot**:

```jsx
// Original CourseList component
const CourseList = ({ courseListData }) => { /* ... */ };

// Adapted for header slot
const CustomHeader = ({ logo, mainMenu, userMenu }) => {
  // Use header-specific props
  return (
    <Header logo={logo} mainMenu={mainMenu}>
      {/* Your customizations */}
    </Header>
  );
};
```

### Adding New Features

**Common Extension Patterns**:

```jsx
// Add new state
const [newFeatureData, setNewFeatureData] = useState([]);

// Add new API calls
useEffect(() => {
  const fetchNewFeatureData = async () => {
    // Your API integration
  };
}, []);

// Add new UI elements
return (
  <Container>
    {/* Existing course list */}
    {/* Your new feature */}
    <YourNewComponent data={newFeatureData} />
  </Container>
);
```

### Component Composition

**Reusable Components**:
```jsx
// Create reusable sub-components
const ArchiveButton = ({ courseId, isArchived, onToggle }) => (
  <Button onClick={() => onToggle(courseId, isArchived)}>
    {isArchived ? 'Unarchive' : 'Archive'}
  </Button>
);

// Use in main component
const CourseList = ({ courseListData }) => (
  <div>
    {courses.map(course => (
      <Card key={course.id}>
        {/* Course info */}
        <ArchiveButton 
          courseId={course.id}
          isArchived={isArchived(course.id)}
          onToggle={handleArchiveToggle}
        />
      </Card>
    ))}
  </div>
);
```

## Troubleshooting

### Common Issues

**Plugin Not Loading**:
- Check `env.config.jsx` slot name matches target slot
- Verify plugin is installed (`npm list @feanil/sample-plugin`)
- Ensure MFE supports the plugin framework version
- Check browser console for JavaScript errors

**Slot Data Issues**:
- Console.log slot props to understand data structure
- Check if slot provides expected data (some slots may not provide certain props)
- Verify slot exists in the MFE version you're using

**API Integration Problems**:
- Verify backend plugin is installed and running
- Check API URLs match backend configuration
- Ensure CORS settings allow frontend-backend communication
- Test API endpoints directly in browser/Postman

**Styling Issues**:
- Use Paragon components for consistent styling
- Check CSS specificity conflicts
- Verify theme variables are available
- Test across different screen sizes

**Development Setup Issues**:
- Ensure `module.config.js` path is correct
- Check that both `env.config.jsx` and `module.config.js` are in MFE root
- Verify file permissions and syntax

### Debugging Techniques

**Console Debugging**:
```jsx
// Add debug logging
console.log("DEBUG: CourseList props:", { courseListData });
console.log("DEBUG: API response:", response.data);
console.log("DEBUG: Archive states:", Array.from(archivedCourses));
```

**React Developer Tools**:
- Use React DevTools to inspect component state
- Check component hierarchy and props
- Monitor state changes during interactions

**Network Debugging**:
- Use browser DevTools Network tab
- Check API request/response details
- Verify authentication headers are present

### Getting Help

1. **Documentation**: Start with [official frontend plugin documentation](https://docs.openedx.org/en/latest/site_ops/how-tos/use-frontend-plugin-slots.html)
2. **MFE-Specific Help**: Check individual MFE repositories for slot documentation
3. **Community**: [Open edX Slack #frontend-platform channel](https://openedx.org/slack)
4. **Issues**: Report bugs in relevant MFE repositories or this sample repository

This frontend plugin demonstrates the power and flexibility of the Open edX Frontend Plugin Framework. By following these patterns, you can create rich customizations that integrate seamlessly with the Open edX ecosystem.