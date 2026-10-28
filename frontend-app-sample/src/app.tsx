import { App, WidgetOperationTypes } from "@openedx/frontend-base";
import CourseList from "./CourseList";

const app: App = {
  appId: "org.openedx.frontend.app.sample",
  slots: [
    {
      slotId: "org.openedx.frontend.slot.learnerDashboard.courseList.v1",
      id: "org.openedx.frontend.widget.sample.courseList.v1",
      op: WidgetOperationTypes.REPLACE,
      relatedId: "defaultContent",
      component: CourseList,
    },
  ],
};

export default app;
