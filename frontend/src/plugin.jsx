import React from 'react';

const CourseList = ({courseListData}) => {
  // Extract the "visibleList"
  const courses = courseListData.visibleList;
  // Render a list of course names
  return (
    <div>
      {courses.map(courseData => (
        <p>
          {courseData.course.courseName}
        </p>
      ))}
    </div>
  )
}

export default CourseList;
