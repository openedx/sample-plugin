import React, { useState, useEffect } from "react";
import { getConfig } from "@edx/frontend-platform";
import { getAuthenticatedHttpClient } from "@edx/frontend-platform/auth";
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

const CourseList = ({ courseListData }) => {
  const [archivedCourses, setArchivedCourses] = useState(new Set());
  const [loadingStates, setLoadingStates] = useState(new Map());

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

  const handleArchiveToggle = async (courseId, isCurrentlyArchived) => {
    console.log(
      `DEBUG: Toggling archive for course ${courseId}, currently archived: ${isCurrentlyArchived}`,
    );

    setLoadingStates((prev) => new Map(prev).set(courseId, true));

    try {
      const client = getAuthenticatedHttpClient();
      const lmsBaseUrl = getConfig().LMS_BASE_URL;
      const url = `${lmsBaseUrl}/sample-plugin/api/v1/course-archive-status/`;

      if (isCurrentlyArchived) {
        // Unarchive: Find existing record and update it
        const listResponse = await client.get(url, {
          params: { course_id: courseId },
        });

        if (listResponse.data.results.length > 0) {
          const existingRecord = listResponse.data.results[0];
          await client.patch(`${url}${existingRecord.id}/`, {
            course_id: courseId,
            is_archived: false,
          });
        }

        // Update local state
        setArchivedCourses((prev) => {
          const newSet = new Set(prev);
          newSet.delete(courseId);
          return newSet;
        });
      } else {
        // Archive: Check if record exists first, then create or update
        const listResponse = await client.get(url, {
          params: { course_id: courseId },
        });

        if (listResponse.data.results.length > 0) {
          // Update existing record
          const existingRecord = listResponse.data.results[0];
          await client.patch(`${url}${existingRecord.id}/`, {
            is_archived: true,
          });
        } else {
          // Create new record
          console.log(
            `DEBUG: Creating new archive record for course ${courseId}`,
          );
          const createResponse = await client.post(url, {
            course_id: courseId,
            is_archived: true,
          });
          console.log(`DEBUG: Create response:`, createResponse.data);
        }

        // Update local state
        console.log(`DEBUG: Adding course ${courseId} to archived set`);
        setArchivedCourses((prev) => {
          const newSet = new Set(prev).add(courseId);
          console.log(`DEBUG: New archived courses set:`, Array.from(newSet));
          return newSet;
        });
      }

      console.log(
        `DEBUG: Successfully ${isCurrentlyArchived ? "unarchived" : "archived"} course ${courseId}`,
      );
    } catch (error) {
      console.error(
        `Failed to ${isCurrentlyArchived ? "unarchive" : "archive"} course:`,
        error,
      );
      console.error("Error details:", {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        message: error.message,
      });
      // Could add toast notification here
    } finally {
      setLoadingStates((prev) => {
        const newMap = new Map(prev);
        newMap.delete(courseId);
        return newMap;
      });
    }
  };

  const renderCourse = (courseData, isArchived = false) => {
    const courseId = courseData.courseRun?.courseId;
    const isLoading = loadingStates.get(courseId);

    return (
      <Col
        key={courseData.cardId}
        xs={12}
        sm={6}
        md={4}
        lg={3}
        className="mb-4"
      >
        <Card>
          <a href={courseData.courseRun?.homeUrl || '#'}>
            <Card.ImageCap
              src={getConfig().LMS_BASE_URL + courseData.course.bannerImgSrc}
              alt={courseData.course.courseName}
            />
          </a>
          <Card.Header
            title={
              <a href={courseData.courseRun?.homeUrl || '#'}>
                {courseData.course.courseName}
              </a>
            }
            subtitle={courseData.course.courseNumber}
            actions={
              <>
                {isArchived && <Badge variant="secondary" className="me-2">Archived</Badge>}
                <Dropdown>
                  <Dropdown.Toggle
                    id={`course-menu-${courseData.cardId}`}
                    as={IconButton}
                    src={MoreVert}
                    iconAs={Icon}
                    variant="primary"
                    aria-label="More actions"
                  />
                  <Dropdown.Menu>
                    {courseData.course.socialShareUrl && (
                      <Dropdown.Item
                        href={courseData.course.socialShareUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        View Course About Page
                      </Dropdown.Item>
                    )}
                  </Dropdown.Menu>
                </Dropdown>
              </>
            }
          />
          <Card.Section>
            {courseData.course.shortDescription && (
              <p className="text-muted small">
                {courseData.course.shortDescription}
              </p>
            )}
          </Card.Section>
          <Card.Footer>
            <Button
              variant={isArchived ? "outline-primary" : "outline-secondary"}
              size="sm"
              disabled={isLoading}
              onClick={() => handleArchiveToggle(courseId, isArchived)}
              iconBefore={
                isLoading ? Spinner : isArchived ? Unarchive : Archive
              }
            >
              {isLoading
                ? "Processing..."
                : isArchived
                  ? "Unarchive"
                  : "Archive"}
            </Button>
          </Card.Footer>
        </Card>
      </Col>
    );
  };

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
