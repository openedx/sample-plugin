import React, { useState, useEffect } from "react";
import { getConfig } from "@edx/frontend-platform";
import { getAuthenticatedHttpClient } from "@edx/frontend-platform/auth";
import { Card, Container, Row, Col, Badge, Collapsible } from "@openedx/paragon";

const CourseList = ({ courseListData }) => {
  const [archivedCourses, setArchivedCourses] = useState(new Set());

  // Safety check for courseListData
  if (!courseListData || !courseListData.visibleList) {
    console.log("DEBUG: courseListData not available yet");
    return <div>Loading courses...</div>;
  }

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

  const renderCourse = (courseData, isArchived = false) => (
    <Col key={courseData.cardId} xs={12} sm={6} md={4} lg={3} className="mb-4">
      <Card>
        <Card.ImageCap
          src={getConfig().LMS_BASE_URL + courseData.course.bannerImgSrc}
          alt={courseData.course.courseName}
        />
        <Card.Header
          title={courseData.course.courseName}
          subtitle={courseData.course.courseNumber}
          actions={isArchived && <Badge variant="secondary">Archived</Badge>}
        />
        <Card.Section>
          {courseData.course.shortDescription && (
            <p className="text-muted small">
              {courseData.course.shortDescription}
            </p>
          )}
        </Card.Section>
      </Card>
    </Col>
  );

  return (
    <Container fluid>
      <Row>
        {activeCourses.map((courseData) => renderCourse(courseData, false))}
      </Row>

      {archivedCoursesList.length > 0 && (
        <div className="mt-5">
          <Collapsible
            title={`Archived Courses (${archivedCoursesList.length})`}
            defaultOpen={false}
          >
            <Row>
              {archivedCoursesList.map((courseData) =>
                renderCourse(courseData, true),
              )}
            </Row>
          </Collapsible>
        </div>
      )}
    </Container>
  );
};

export default CourseList;
