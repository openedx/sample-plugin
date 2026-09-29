# Frontend App Implementation Guide (frontend-base)

This directory contains a sample [frontend-base](https://github.com/openedx/frontend-base) **app** that customizes the learner-dashboard's course list with archive/unarchive functionality.

It is published to npm as `@openedx/frontend-app-sample` and plugged into a frontend-base site via the site config.

> [!NOTE]
> This is the frontend-base sibling of [`../frontend-plugin-sample/`](../frontend-plugin-sample/), which targets the legacy `frontend-plugin-framework` (FPF) flow. The Tutor plugin in [`../tutor-contrib-sample/`](../tutor-contrib-sample/) registers both. See the [porting guide](https://docs.openedx.org/en/latest/site_ops/how-tos/port-frontend-plugin-to-frontend-base.html) for the differences between the two.

## Table of Contents

- [Overview](#overview)
- [How a frontend-base app works](#how-a-frontend-base-app-works)
- [Code Walkthrough](#code-walkthrough)
- [Local Development](#local-development)
- [Deployment with Tutor](#deployment-with-tutor)
- [Customizing this Example](#customizing-this-example)
- [Migrating from frontend-plugin-framework](#migrating-from-frontend-plugin-framework)
- [Troubleshooting](#troubleshooting)

## Overview

The plugin demonstrates how to extend an Open edX MFE without forking it:

- **`CourseList.tsx`** is a React component that fetches archive state from the backend plugin's API and renders an archive-aware version of the learner-dashboard course list.
- **`app.tsx`** exports a frontend-base `App` that registers a single `widgetReplace` operation against the learner-dashboard's `CourseList` slot.

Once the site config includes `sampleApp` in its `apps` list, the operation is applied automatically wherever the slot renders. No edits to the learner-dashboard repo are required.

**Official Documentation:**
- [frontend-base on GitHub](https://github.com/openedx/frontend-base)
- [tutor-mfe: Frontend-base site](https://github.com/overhangio/tutor-mfe#frontend-base-site) (covers `FRONTEND_APPS`, `FRONTEND_SLOTS`, and app-package patterns)
- [Available slots in frontend-app-learner-dashboard](https://github.com/openedx/frontend-app-learner-dashboard/tree/master/src/slots)

## How a frontend-base app works

An `App` is a TypeScript/JavaScript object exported from an npm package. Its key fields:

| Field | Purpose |
| --- | --- |
| `appId` | A globally-unique reverse-DNS string identifying the App. |
| `slots` | An array of `SlotOperation` objects that mutate the site's slots when the App is registered. |
| `routes` | (Optional) Routes the App contributes to the shell. Not used in this sample. |
| `providers` | (Optional) React context providers wrapped around the shell. |
| `config` | (Optional) Default values for app-specific runtime config keys. |

A `SlotOperation` describes one mutation:

```js
{
  slotId: 'org.openedx.frontend.slot.learnerDashboard.courseList.v1',
  id: 'org.openedx.frontend.widget.sample.courseList.v1',
  op: WidgetOperationTypes.REPLACE,
  relatedId: 'defaultContent',
  component: CourseList,
}
```

| Field | Purpose |
| --- | --- |
| `slotId` | Which slot to target. Each MFE documents its slot IDs under `src/slots/`. |
| `id` | A unique reverse-DNS id for this widget. |
| `op` | One of `APPEND`, `PREPEND`, `INSERT_BEFORE`, `INSERT_AFTER`, `REPLACE`, `REMOVE`. |
| `relatedId` | The widget to anchor against. `defaultContent` refers to the slot's default rendering. |
| `component` | A React component that receives the slot's props. Use `element` instead for inline JSX. |
| `condition` | (Optional) `{ active: [roleId] }` to scope the op to specific routes. |

This is **different** from the legacy `frontend-plugin-framework` API, which used `PLUGIN_OPERATIONS.Insert/Hide/Wrap` with a `widget` wrapper and was configured via `env.config.jsx`. See [Migrating from frontend-plugin-framework](#migrating-from-frontend-plugin-framework) below.

## Code Walkthrough

### `src/CourseList.tsx`

The React component. It calls the backend plugin's REST API using frontend-base's auth client and config helpers:

```jsx
import { getAuthenticatedHttpClient, getSiteConfig } from "@openedx/frontend-base";

const client = getAuthenticatedHttpClient();
const lmsBaseUrl = getSiteConfig().lmsBaseUrl;
```

The slot delivers a `courseListData` prop with `visibleList`, `course`, and `courseRun` fields. The component splits courses into active/archived buckets and renders Paragon cards with an archive toggle that PATCHes the backend.

### `src/app.tsx`

Declares the App and its single slot operation. The op uses `WidgetOperationTypes.REPLACE` with `relatedId: 'defaultContent'` so the upstream default course list is hidden and ours takes its place.

### `src/index.ts`

Re-exports the App as the default and the underlying React component as a named export, so site operators can `addApp(siteConfig, sampleApp)` and tests can mount `<CourseList />` directly.

## Local Development

### Develop the App inside a site

The most ergonomic loop is to wire this package into a frontend-base site as a local workspace package so the site's bundler hot-reloads changes:

1. Clone [`frontend-template-site`](https://github.com/openedx/frontend-template-site) locally. It is the standard starting point for a frontend-base site.
2. Put a copy of this package (or a bind-mount, but never a symlink) under the site's `packages/` directory, add `"@openedx/frontend-app-sample": "*"` to the site's `package.json` `dependencies`, then run `npm install` in the site root so npm picks it up as a workspace.
3. In the site's `site.config.dev.tsx`:

   ```tsx
   import { EnvironmentTypes, SiteConfig, footerApp, headerApp, shellApp } from '@openedx/frontend-base';
   import { learnerDashboardApp } from '@openedx/frontend-app-learner-dashboard';
   import { sampleApp } from '@openedx/frontend-app-sample';

   const siteConfig: SiteConfig = {
     // ... siteId, baseUrl, lmsBaseUrl, etc. ...
     environment: EnvironmentTypes.DEVELOPMENT,
     apps: [shellApp, headerApp, footerApp, learnerDashboardApp, sampleApp],
   };

   export default siteConfig;
   ```

4. Run `npm run dev:packages` in the site root. It builds the workspace packages via turbo, watches them, and starts the site dev server in one shot.

### Develop the App via tutor-mfe

If you'd rather develop against a Tutor stack, and provided the sibling [`tutor-contrib-sample`](../tutor-contrib-sample/) plugin is installed and enabled:

```bash
tutor mounts add /path/to/sample-plugin/frontend-app-sample
tutor dev launch
```

The `mfe-dev` service bind-mounts the package into the site's workspace and watches for changes. The site is served at `http://apps.local.openedx.io:8080`.

### Build for publish

```bash
npm install
npm run build
```

The output goes to `dist/`. The package is publishable to npm as `@openedx/frontend-app-sample`.

## Deployment with Tutor

In production, the package is installed into the frontend-base site by [`tutor-contrib-sample`](../tutor-contrib-sample/), which:

1. Adds an entry to `FRONTEND_APPS` so tutor-mfe installs the npm package into the site workspace.
2. Adds an `mfe-site-config-imports` patch to import the App.
3. Adds an `mfe-site-config` patch to call `addApp(siteConfig, sampleApp)`.

See [`../tutor-contrib-sample/README.md`](../tutor-contrib-sample/README.md) for the full plugin.

## Customizing this Example

**Target a different slot:** Replace the `slotId` in `src/app.tsx`. The available slot IDs are documented under each frontend-base app's `src/slots/` directory (e.g., the [learner-dashboard slots](https://github.com/openedx/frontend-app-learner-dashboard/tree/master/src/slots)).

**Use a different operation:** Swap `WidgetOperationTypes.REPLACE` for `APPEND`, `PREPEND`, `INSERT_BEFORE`, `INSERT_AFTER`, or `REMOVE`. With `APPEND`/`PREPEND`, drop `relatedId` and the default content stays alongside your widget.

**Scope to specific routes:** Add a `condition: { active: ['org.openedx.frontend.role.learnerDashboard'] }` to the op so it only fires on the learner-dashboard routes. Useful when the same slot is rendered by multiple apps.

**Register multiple ops:** Push more entries into the App's `slots` array. They can target the same or different slots.

## Troubleshooting

**App registers but the slot doesn't change:** Confirm the `slotId` matches the target frontend-base app's slot. Slot IDs changed during the FPF -> frontend-base migration (e.g., `org.openedx.frontend.learner_dashboard.course_list.v1` -> `org.openedx.frontend.slot.learnerDashboard.courseList.v1`).

**`getConfig is not a function` or similar at runtime:** Your code is still importing from `@edx/frontend-platform`. Swap to `@openedx/frontend-base`. If you can't change the source, install [frontend-base-compat](https://github.com/openedx/frontend-base-compat) instead.

**App leaks into another MFE's routes:** Add `condition: { active: [roleId] }` to the op, with the role registered by the target app (e.g., `org.openedx.frontend.role.learnerDashboard`).

**The default course list still renders alongside mine:** Your op is probably `APPEND`/`PREPEND`, which keeps `defaultContent`. Use `REPLACE` with `relatedId: 'defaultContent'` to swap it for yours instead.
