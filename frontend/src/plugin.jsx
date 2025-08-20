import React from 'react';
import {getConfig} from '@edx/frontend-platform';

const CourseList = ({courseListData}) => {
  // Extract the "visibleList"
  const courses = courseListData.visibleList;
  // Render a list of course names
  return (
    <div>
      {courses.map(courseData => (
        <>
        <h2>
          {courseData.course.courseName}
          <img src={getConfig().LMS_BASE_URL + courseData.course.bannerImgSrc}></img>
        </h2>
          {console.log(courseData.cardId)}
        </>
      ))}
    </div>
  )
}

export default CourseList;
