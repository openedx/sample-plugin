// @@TODO: add tests.
import React from "react";
import { Icon } from "@openedx/paragon";
import { Star } from "@openedx/paragon/icons";

// Reads `averageStars` / `ratingCount` off a courseRun object. Those two fields
// are injected into each courseRun by the backend plugin's filter pipeline
// step (AddAverageRatingToLearnerHomeCourseRun), so any consumer that hands us
// the courseRun from the Learner Home /init response will Just Work.
const CourseCardRating = ({ courseRun }) => {
  const averageStars = courseRun?.averageStars ?? null;
  const ratingCount = courseRun?.ratingCount ?? 0;

  return (
    <div className="d-flex align-items-center small text-muted mt-2">
      <Icon src={Star} className="me-1" />
      {ratingCount > 0 && (
        <span className="me-2">{averageStars.toFixed(1)}</span>
      )}
      <span>
        ({ratingCount} {ratingCount === 1 ? "rating" : "ratings"})
      </span>
    </div>
  );
};

export default CourseCardRating;
