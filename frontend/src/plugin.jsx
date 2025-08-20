import React, { useState, useEffect } from "react";
import { getConfig } from "@edx/frontend-platform";
import { getAuthenticatedHttpClient } from "@edx/frontend-platform/auth";

const CourseList = ({ courseListData }) => {
  const [archivedCourses, setArchivedCourses] = useState(new Set());

  // Extract the "visibleList"
  const courses = courseListData.visibleList;

  // Log the full course data structure for debugging
  console.log("DEBUG: Full courseListData structure:", courseListData);
  console.log("DEBUG: First course data object:", courses?.[0]);

  useEffect(() => {
    const fetchArchivedCourses = async () => {
      try {
        const client = getAuthenticatedHttpClient();
        const lmsBaseUrl = getConfig().LMS_BASE_URL;
        console.log(
          "DEBUG: Fetching archived courses from:",
          `${lmsBaseUrl}/sample-plugin/api/v1/course-archive-status/`,
        );

        const response = await client.get(
          `${lmsBaseUrl}/sample-plugin/api/v1/course-archive-status/`,
          {
            params: { is_archived: true },
          },
        );

        console.log("DEBUG: Archived courses API response:", response.data);

        const archivedCourseIds = new Set(
          response.data.results.map((item) => item.course_id),
        );

        console.log(
          "DEBUG: Archived course IDs from API:",
          Array.from(archivedCourseIds),
        );
        setArchivedCourses(archivedCourseIds);
      } catch (error) {
        console.error("Failed to fetch archived courses:", error);
      }
    };

    fetchArchivedCourses();
  }, []);

  // Log course IDs we're trying to match against
  console.log("DEBUG: Course IDs from course data:");
  courses.forEach((courseData, index) => {
    console.log(`Course ${index}:`, {
      cardId: courseData.cardId,
      "courseRun.courseId": courseData.courseRun?.courseId,
      "courseRun object keys": Object.keys(courseData.courseRun || {}),
      "full courseRun object": courseData.courseRun,
    });
  });

  console.log(
    "DEBUG: Archived course IDs to match:",
    Array.from(archivedCourses),
  );

  // Separate courses into active and archived
  const activeCourses = courses.filter((courseData) => {
    const courseId = courseData.courseRun?.courseId;
    const isArchived = archivedCourses.has(courseId);
    console.log(
      `DEBUG: Course "${courseData.course?.courseName}" (ID: ${courseId}) - archived: ${isArchived}`,
    );
    return !isArchived;
  });

  const archivedCoursesList = courses.filter((courseData) => {
    const courseId = courseData.courseRun?.courseId;
    return archivedCourses.has(courseId);
  });

  console.log("DEBUG: Active courses count:", activeCourses.length);
  console.log("DEBUG: Archived courses count:", archivedCoursesList.length);

  const renderCourse = (courseData) => (
    <div key={courseData.cardId}>
      <h2>
        {courseData.course.courseName}
        <img
          src={getConfig().LMS_BASE_URL + courseData.course.bannerImgSrc}
          alt={courseData.course.courseName}
        ></img>
      </h2>
    </div>
  );

  return (
    <div>
      {activeCourses.map(renderCourse)}

      {archivedCoursesList.length > 0 && (
        <div>
          <h2>Archived Courses</h2>
          {archivedCoursesList.map(renderCourse)}
        </div>
      )}
    </div>
  );
};

export default CourseList;
