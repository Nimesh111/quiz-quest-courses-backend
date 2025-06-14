from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from app.models import Course, CourseCreate, CourseUpdate, CourseEnrollment, User
from app.database import db
from app.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[Course])
async def get_courses(
    category: Optional[str] = Query(None, description="Filter by category"),
    level: Optional[str] = Query(None, description="Filter by difficulty level"),
    search: Optional[str] = Query(None, description="Search in title and description")
):
    """Get all courses with optional filtering"""
    courses = db.read_all("courses")
    
    # Convert to Course objects
    course_list = [Course(**course) for course in courses]
    
    # Apply filters
    if category:
        course_list = [c for c in course_list if c.category.lower() == category.lower()]
    
    if level:
        course_list = [c for c in course_list if c.level.lower() == level.lower()]
    
    if search:
        search_term = search.lower()
        course_list = [
            c for c in course_list 
            if search_term in c.title.lower() or search_term in c.description.lower()
        ]
    
    return course_list

@router.get("/{course_id}", response_model=Course)
async def get_course(course_id: int):
    """Get course by ID"""
    course = db.read("courses", course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return Course(**course)

@router.post("/", response_model=Course, status_code=status.HTTP_201_CREATED)
async def create_course(
    course: CourseCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new course (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    course_data = course.dict()
    created_course = db.create("courses", course_data)
    
    return Course(**created_course)

@router.post("/{course_id}/enroll", response_model=CourseEnrollment)
async def enroll_in_course(
    course_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Enroll in a course"""
    # Check if course exists
    course = db.read("courses", course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if already enrolled
    enrollments = db.find_by_field("enrollments", "user_id", current_user.id)
    existing_enrollment = next((e for e in enrollments if e.get("course_id") == course_id), None)
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this course"
        )
    
    # Create enrollment
    enrollment_data = {
        "user_id": current_user.id,
        "course_id": course_id,
        "progress": 0.0
    }
    
    enrollment = db.create("enrollments", enrollment_data)
    
    # Update course student count
    current_students = course.get("students", 0)
    db.update("courses", course_id, {"students": current_students + 1})
    
    return CourseEnrollment(**enrollment) 