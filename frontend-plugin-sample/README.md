# frontend-plugin-sample

A React component that replaces the learner-dashboard's course list with one that supports archiving courses. Wired into the `org.openedx.frontend.learner_dashboard.course_list.v1` plugin slot. Reads each course's archive state from a filter-injected slot prop and writes back to the [`backend-plugin-sample`](../backend-plugin-sample/) REST API on toggle.

> [!NOTE]
> This is the legacy frontend-plugin-framework sibling of [`../frontend-app-sample/`](../frontend-app-sample/), which targets the newer [`frontend-base`](https://github.com/openedx/frontend-base) stack. The Tutor plugin in [`../tutor-contrib-sample/`](../tutor-contrib-sample/) registers both; this one is the active path when the frontend-base learner-dashboard App is *not* enabled in tutor-mfe, the frontend-base sibling otherwise. See the [porting guide](https://docs.openedx.org/en/latest/site_ops/how-tos/port-frontend-plugin-to-frontend-base.html) for the differences between the two.

## How to use it

See the root [README](../README.md) for setup instructions. With Tutor, [`tutor-contrib-sample`](../tutor-contrib-sample/) installs the published npm package and wires it into the learner-dashboard slot. For local source development (with or without Tutor), the MFE-side files in [Local development setup](#local-development-setup) below are required.

## How it works

**The component.** [`src/plugin.jsx`](./src/plugin.jsx) exports `CourseList`, a Paragon-styled replacement for the learner-dashboard's default course list. It receives `courseListData` (`visibleList`, `filterOptions`, etc.) as a slot prop.

**Reading archive state without an extra API call.** The initial archive flag is read directly from each course run as `courseRun.isArchivedByLearner`. That field is injected into the learner-dashboard's `/init` response by the backend plugin's filter ([`pipeline.py`](../backend-plugin-sample/src/openedx_plugin_sample/pipeline.py)), which saves a round-trip on every dashboard load and keeps the archive state consistent with the rest of the course data from the same response. The REST API is still used for writes when the learner clicks archive/unarchive.

**Authentication and config.** Writes go through `getAuthenticatedHttpClient()` from `@edx/frontend-platform/auth`, and the LMS origin comes from `getConfig().LMS_BASE_URL`. UI components are from [Paragon](https://paragon-openedx.netlify.app/).

## Local development setup

Two files go in your MFE checkout root (e.g. `frontend-app-learner-dashboard/`), neither committed:

**`module.config.js`** — tells the MFE's webpack to resolve `@openedx/plugin-sample` to your local source tree instead of `node_modules`:

```js
module.exports = {
  localModules: [
    {
      moduleName: '@openedx/plugin-sample',
      dir: '/absolute/path/to/sample-plugin/frontend-plugin-sample',
      dist: 'src',
    },
  ],
};
```

**`env.config.jsx`** — plugs the component into the slot:

```jsx
import { DIRECT_PLUGIN, PLUGIN_OPERATIONS } from '@openedx/frontend-plugin-framework';
import { CourseList } from '@openedx/plugin-sample';

const config = {
  pluginSlots: {
    'org.openedx.frontend.learner_dashboard.course_list.v1': {
      keepDefault: false,
      plugins: [
        {
          op: PLUGIN_OPERATIONS.Insert,
          widget: {
            id: 'custom_course_list',
            type: DIRECT_PLUGIN,
            priority: 60,
            RenderWidget: CourseList,
          },
        },
      ],
    },
  },
};

export default config;
```

Then, from the MFE checkout:

```bash
npm ci

# With Tutor — point tutor-mfe at your local MFE devserver:
tutor mounts add .
tutor dev reboot -d mfe
npm run dev

# Without Tutor:
npm start
```
