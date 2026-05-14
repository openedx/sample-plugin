# Frontend Plugin Implementation Guide

This directory contains React components that demonstrate how to customize Open edX micro-frontends (MFEs) using the Frontend Plugin Framework. Two features are wired up side by side:

- **Archive** — `CourseList` replaces the default course list on the learner-dashboard with one that adds per-learner archive/unarchive controls.
- **Rating** — `RateThisContent` slots a 1-5 star widget below each unit in `frontend-app-learning`; `CourseCardRating` (used internally by `CourseList`) shows the resulting per-course average on each card.

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

This frontend plugin demonstrates **Open edX MFE customization** using the Frontend Plugin Framework against slots in two different MFEs.

**What this plugin provides:**
- **Custom CourseList Component**: Enhanced course display with archive functionality and inline per-course rating
- **RateThisContent Component**: Per-unit 1-5 star rating widget for the learning MFE
- **Backend API Integration**: Connects to the sample backend plugin APIs
- **Slot Replacement and Insert Patterns**: Demonstrates both fully replacing a slot's default contents and inserting a new widget into a host slot
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

#### 2. Backend Data via the Filter Pipeline

Rather than firing extra GETs for each card on every dashboard load, the
initial archive state *and* the per-course average rating are read directly off
the slot props. The backend plugin runs two filter pipeline steps (see
[`pipeline.py`](../backend-plugin-sample/src/openedx_plugin_sample/pipeline.py))
that inject extra keys onto each courseRun in the Learner Home `/init` response:

- `isArchivedByLearner` (bool) — does the requesting user have this course archived?
- `averageStars` (float or null) — cached per-course rating average
- `ratingCount` (int) — number of unit ratings backing that average

The component reads them straight off the slot props:

```jsx
const [archivedCourses, setArchivedCourses] = useState(() => {
  const initial = new Set();
  (courseListData?.visibleList || []).forEach((courseData) => {
    if (courseData.courseRun?.isArchivedByLearner) {
      initial.add(courseData.courseRun.courseId);
    }
  });
  return initial;
});

// And inside each card:
<CourseCardRating courseRun={courseData.courseRun} />
```

**Why this pattern**: One fewer round-trip per dashboard load, and the injected
state stays consistent with the rest of the course data from the same response.
The REST API is still used for writes (archive/unarchive, submit rating) — see
the toggle handler below.

**Key Patterns:**
- **Filter-injected data**: Read `courseRun.isArchivedByLearner` / `averageStars` / `ratingCount` straight from slot props
- **Authentication** (for writes): `getAuthenticatedHttpClient()` handles Open edX auth
- **Configuration**: `getConfig().LMS_BASE_URL` gets platform URLs

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

This plugin targets two slots, in two different MFEs:

| Slot ID | MFE | Component | Operation |
|---------|-----|-----------|-----------|
| `org.openedx.frontend.learner_dashboard.course_list.v1` | `frontend-app-learner-dashboard` | `CourseList` | `Hide` default widget + `Insert` ours |
| `org.openedx.frontend.learning.sequence_container.v1` | `frontend-app-learning` | `RateThisContent` | `Insert` ours alongside default |

### CourseList slot (Hide + Insert)

The default `default_contents` widget is hidden so it doesn't render *next to*
our replacement. We then insert our `CourseList` widget into the same slot:

```javascript
'org.openedx.frontend.learner_dashboard.course_list.v1': {
  plugins: [
    {
      op: PLUGIN_OPERATIONS.Hide,
      widgetId: 'default_contents',
    },
    {
      op: PLUGIN_OPERATIONS.Insert,
      widget: {
        id: 'openedx_plugin_sample_course_list',
        type: DIRECT_PLUGIN,
        priority: 50,
        RenderWidget: CourseList,
      },
    },
  ],
},
```

### RateThisContent slot (Insert only)

The learning MFE's sequence-container slot has no widget we need to displace,
so a single `Insert` is enough:

```javascript
'org.openedx.frontend.learning.sequence_container.v1': {
  plugins: [
    {
      op: PLUGIN_OPERATIONS.Insert,
      widget: {
        id: 'openedx_plugin_sample_rate_this_content',
        type: DIRECT_PLUGIN,
        priority: 50,
        RenderWidget: RateThisContent,
      },
    },
  ],
},
```

### Plugin Configuration Options

| Option | Purpose | Values |
|--------|---------|--------|
| **op** | Plugin operation type | `Insert`, `Hide`, `Modify`, `Wrap`, `Replace` |
| **widgetId** | Identifies which existing widget to act on (for `Hide`/`Modify`/`Wrap`/`Replace`) | The host slot's widget ID, often `'default_contents'` |
| **priority** | Loading order within the slot | Higher numbers render later |
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

1. **Tutor & Tutor-MFE Setup**: Tutor is installed and launched in `dev` mode.
2. **Backend Plugin**: Install the backend plugin (see [`../backend-plugin-sample/README.md`](../backend-plugin-sample/README.md))
3. **Node.js**: Version 16+ with npm or yarn

### Local Development Setup

The plugin's two slots live in two different MFEs:

- `frontend-app-learner-dashboard` — for the Archive `CourseList` (and the
  embedded per-course rating display)
- `frontend-app-learning` — for the per-unit `RateThisContent` widget

You only need to write the `module.config.js` and `env.config.jsx` files once,
then drop a copy of each into the root of every MFE you want to customize.

#### Step 1: Create `module.config.js` (per MFE)

In the MFE root, create `module.config.js` (do not commit it). This tells the
MFE's webpack to load `@openedx/plugin-sample` from your local checkout instead
of from npm, so you can iterate on the plugin without publishing:

```javascript
module.exports = {
  localModules: [
    {
      moduleName: '@openedx/plugin-sample',
      dir: '/path/to/sample-plugin/frontend-plugin-sample',
      dist: 'src',
    },
  ],
};
```

#### Step 2: Create a shared `env.config.jsx` and drop a copy into each MFE

`env.config.jsx` is how each MFE resolves its plugin-slot configuration at
build/runtime. A given MFE only acts on the slots it actually owns and silently
ignores the rest, so the easiest thing for development is to keep **one
`env.config.jsx`** that lists every slot this plugin targets and copy the same
file into each MFE root you're customizing.

```jsx
// env.config.jsx -- copy this file into the root of every MFE you want to
// customize (frontend-app-learner-dashboard, frontend-app-learning, ...).
// Each MFE only acts on the slots it owns and ignores the others.

import { DIRECT_PLUGIN, PLUGIN_OPERATIONS } from '@openedx/frontend-plugin-framework';
import { CourseList, RateThisContent } from '@openedx/plugin-sample';

const config = {
  pluginSlots: {
    // Lives in: frontend-app-learner-dashboard
    // Effect: hides the default course list and renders our archive-aware one,
    // which also displays the per-course rating injected by the backend filter.
    'org.openedx.frontend.learner_dashboard.course_list.v1': {
      plugins: [
        {
          op: PLUGIN_OPERATIONS.Hide,
          widgetId: 'default_contents',
        },
        {
          op: PLUGIN_OPERATIONS.Insert,
          widget: {
            id: 'openedx_plugin_sample_course_list',
            type: DIRECT_PLUGIN,
            priority: 50,
            RenderWidget: CourseList,
          },
        },
      ],
    },

    // Lives in: frontend-app-learning
    // Effect: inserts a "Rate this content" widget below each unit.
    'org.openedx.frontend.learning.sequence_container.v1': {
      plugins: [
        {
          op: PLUGIN_OPERATIONS.Insert,
          widget: {
            id: 'openedx_plugin_sample_rate_this_content',
            type: DIRECT_PLUGIN,
            priority: 50,
            RenderWidget: RateThisContent,
          },
        },
      ],
    },
  },
};

export default config;
```

Do not commit `env.config.jsx` into the MFE repos — it's your local override.

**Notes:**
- Slot IDs are fully qualified (`org.openedx.frontend.<mfe>.<slot_name>.v<n>`).
  Don't use the short names you sometimes see in older docs — those won't match.
- Use `PLUGIN_OPERATIONS.Hide` + `Insert` to fully replace a slot's default
  widget. `keepDefault: false` (an older alternative) works in some slot
  versions but the Hide/Insert pattern is what the Tutor plugin in this repo
  emits, so the dev and prod configurations stay consistent.
- The plugin's npm package is `@openedx/plugin-sample`. Step 1's
  `module.config.js` is what makes that import resolve to your local source.

#### Step 3: Start the MFE dev server

From the MFE repository root:

```bash
# Install MFE dependencies (just once).
npm ci

# If you're running Tutor, point its MFE container at your local devserver:
tutor mounts add .
tutor dev reboot -d mfe

# Then run the MFE devserver itself:
npm run dev        # if running under Tutor
# or
npm start          # if running standalone (no Tutor)
```

Repeat for the second MFE if you want to develop both features at once.

### Development vs Production Configuration

**Local Development**:
- One shared `env.config.jsx` that lists every slot this plugin targets,
  copied into each MFE root you want to customize
- A matching `module.config.js` in each MFE root, pointing at your local checkout
- Hot reload via `npm run dev` / `npm start`

**Production Deployment**:
- Equivalent slot configuration is emitted by the Tutor plugin
  ([`tutor-contrib-sample/tutorsample/plugin.py`](../tutor-contrib-sample/tutorsample/plugin.py))
  via `PLUGIN_SLOTS.add_item(...)`
- The plugin is installed as the published `@openedx/plugin-sample` npm package
- Optimized production builds; no local-source mounting

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

**Tutor Plugin Configuration** (see [`../tutor-contrib-sample/README.md`](../tutor-contrib-sample/README.md)):

```python
from tutormfe.hooks import PLUGIN_SLOTS

# Archive: replace the default course list on the learner dashboard.
PLUGIN_SLOTS.add_item((
    "learner-dashboard",
    "org.openedx.frontend.learner_dashboard.course_list.v1",
    """
    {
      op: PLUGIN_OPERATIONS.Hide,
      widgetId: 'default_contents',
    },
    {
      op: PLUGIN_OPERATIONS.Insert,
      widget: {
        id: 'openedx_plugin_sample_course_list',
        type: DIRECT_PLUGIN,
        priority: 50,
        RenderWidget: CourseList,
      },
    }""",
))

# Rating: add the per-unit rating widget to the learning MFE.
PLUGIN_SLOTS.add_item((
    "learning",
    "org.openedx.frontend.learning.sequence_container.v1",
    """
    {
      op: PLUGIN_OPERATIONS.Insert,
      widget: {
        id: 'openedx_plugin_sample_rate_this_content',
        type: DIRECT_PLUGIN,
        priority: 50,
        RenderWidget: RateThisContent,
      },
    }""",
))
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
- Verify plugin is installed (`npm list @openedx/plugin-sample`)
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
