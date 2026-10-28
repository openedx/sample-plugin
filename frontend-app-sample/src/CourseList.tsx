import { useState } from "react";
import { getAuthenticatedHttpClient, getSiteConfig } from "@openedx/frontend-base";
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

// The shape the learner-dashboard slot delivers.  We declare only the fields
// this widget reads; everything else is left out so additions upstream are
// a non-event for our types.
interface CourseData {
  cardId: string;
  course: {
    courseName: string;
    courseNumber: string;
    bannerImgSrc: string;
    socialShareUrl?: string;
    shortDescription?: string;
  };
  courseRun?: {
    courseId: string;
    homeUrl?: string;
    // Injected into each courseRun by the backend plugin's filter pipeline
    // step on the Learner Home /init API response.
    isArchivedByLearner?: boolean;
  };
}

interface CourseListData {
  visibleList: CourseData[];
}

interface CourseListProps {
  courseListData?: CourseListData;
}

interface ArchiveStatusRecord {
  id: number;
  course_id: string;
  is_archived: boolean;
}

const CourseList = ({ courseListData }: CourseListProps) => {
  // Seed the archived-course set from `courseRun.isArchivedByLearner`, which the
  // backend plugin's filter pipeline injects into each courseRun in the Learner
  // Home /init API response. This avoids a separate GET to course-archive-status
  // on every dashboard load. Local toggles below keep this set in sync without
  // a refetch.
  const [archivedCourses, setArchivedCourses] = useState<Set<string>>(() => {
    const initial = new Set<string>();
    (courseListData?.visibleList || []).forEach((courseData) => {
      if (courseData.courseRun?.isArchivedByLearner) {
        initial.add(courseData.courseRun.courseId);
      }
    });
    return initial;
  });
  const [loadingStates, setLoadingStates] = useState<Map<string, boolean>>(new Map());

  if (!courseListData || !courseListData.visibleList) {
    return <div>Loading courses...</div>;
  }

  const courses = courseListData.visibleList;

  const activeCourses = courses.filter(
    (courseData) => {
      const courseId = courseData.courseRun?.courseId;
      return !courseId || !archivedCourses.has(courseId);
    },
  );

  const archivedCoursesList = courses.filter((courseData) => {
    const courseId = courseData.courseRun?.courseId;
    return courseId !== undefined && archivedCourses.has(courseId);
  });

  const handleArchiveToggle = async (courseId: string, isCurrentlyArchived: boolean) => {
    setLoadingStates((prev) => new Map(prev).set(courseId, true));

    try {
      const client = getAuthenticatedHttpClient();
      const lmsBaseUrl = getSiteConfig().lmsBaseUrl;
      const url = `${lmsBaseUrl}/sample-plugin/api/v1/course-archive-status/`;

      const listResponse = await client.get<{ results: ArchiveStatusRecord[] }>(url, {
        params: { course_id: courseId },
      });

      if (listResponse.data.results.length > 0) {
        const existingRecord = listResponse.data.results[0];
        await client.patch(`${url}${existingRecord.id}/`, {
          is_archived: !isCurrentlyArchived,
        });
      } else {
        await client.post(url, {
          course_id: courseId,
          is_archived: !isCurrentlyArchived,
        });
      }

      setArchivedCourses((prev) => {
        const newSet = new Set(prev);
        if (isCurrentlyArchived) {
          newSet.delete(courseId);
        } else {
          newSet.add(courseId);
        }
        return newSet;
      });
    } catch (error) {
      console.error(
        `Failed to ${isCurrentlyArchived ? "unarchive" : "archive"} course:`,
        error,
      );
    } finally {
      setLoadingStates((prev) => {
        const newMap = new Map(prev);
        newMap.delete(courseId);
        return newMap;
      });
    }
  };

  const renderCourse = (courseData: CourseData, isArchived = false) => {
    const courseId = courseData.courseRun?.courseId;
    const isLoading = courseId !== undefined && loadingStates.get(courseId);

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
              src={getSiteConfig().lmsBaseUrl + courseData.course.bannerImgSrc}
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
              onClick={() => courseId && handleArchiveToggle(courseId, isArchived)}
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
