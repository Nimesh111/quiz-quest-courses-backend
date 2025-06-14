from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from app.models import DashboardStats, SearchResults, User, Course, Tutorial, Article, Quiz
from app.database import db
from app.auth import get_current_active_user

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: User = Depends(get_current_active_user)):
    """Get comprehensive dashboard statistics for the user"""
    
    # Get enrollments
    enrollments = db.find_by_field("enrollments", "user_id", current_user.id)
    enrolled_courses = len(enrollments)
    completed_courses = len([e for e in enrollments if e.get("completed_at")])
    
    # Get tutorial completions
    completions = db.find_by_field("completions", "user_id", current_user.id)
    completed_tutorials = len(completions)
    total_tutorials = len(db.read_all("tutorials"))
    
    # Get article interactions
    bookmarks = db.find_by_field("bookmarks", "user_id", current_user.id)
    likes = db.find_by_field("likes", "user_id", current_user.id)
    bookmarked_articles = len(bookmarks)
    read_articles = len(likes)  # Using likes as a proxy for read articles
    
    # Get quiz attempts
    quiz_attempts = db.find_by_field("quiz_attempts", "user_id", current_user.id)
    total_quiz_attempts = len(quiz_attempts)
    
    # Calculate average quiz score
    if quiz_attempts:
        average_quiz_score = sum(attempt.get("score", 0) for attempt in quiz_attempts) / len(quiz_attempts)
    else:
        average_quiz_score = 0
    
    # Estimate study hours (simplified calculation)
    study_hours = (completed_courses * 15) + (completed_tutorials * 2) + (total_quiz_attempts * 1)
    
    # Count certificates (completed courses)
    certificates = completed_courses
    
    return DashboardStats(
        enrolled_courses=enrolled_courses,
        completed_courses=completed_courses,
        study_hours=study_hours,
        certificates=certificates,
        completed_tutorials=completed_tutorials,
        total_tutorials=total_tutorials,
        read_articles=read_articles,
        bookmarked_articles=bookmarked_articles,
        quiz_attempts=total_quiz_attempts,
        average_quiz_score=round(average_quiz_score, 2)
    )

@router.get("/my-courses")
async def get_my_courses(current_user: User = Depends(get_current_active_user)):
    """Get user's enrolled courses with progress"""
    enrollments = db.find_by_field("enrollments", "user_id", current_user.id)
    
    # Get course details
    courses = []
    all_courses = db.read_all("courses")
    course_dict = {course["id"]: course for course in all_courses}
    
    for enrollment in enrollments:
        course_id = enrollment.get("course_id")
        if course_id in course_dict:
            course_data = course_dict[course_id].copy()
            course_data["enrollment"] = enrollment
            courses.append(course_data)
    
    return courses

@router.get("/my-tutorials")
async def get_my_tutorials(current_user: User = Depends(get_current_active_user)):
    """Get user's completed tutorials"""
    completions = db.find_by_field("completions", "user_id", current_user.id)
    
    # Get tutorial details
    tutorials = []
    all_tutorials = db.read_all("tutorials")
    tutorial_dict = {tutorial["id"]: tutorial for tutorial in all_tutorials}
    
    for completion in completions:
        tutorial_id = completion.get("tutorial_id")
        if tutorial_id in tutorial_dict:
            tutorial_data = tutorial_dict[tutorial_id].copy()
            tutorial_data["completion"] = completion
            tutorials.append(tutorial_data)
    
    return tutorials

@router.get("/my-articles")
async def get_my_articles(current_user: User = Depends(get_current_active_user)):
    """Get user's bookmarked and liked articles"""
    bookmarks = db.find_by_field("bookmarks", "user_id", current_user.id)
    likes = db.find_by_field("likes", "user_id", current_user.id)
    
    # Get article details
    all_articles = db.read_all("articles")
    article_dict = {article["id"]: article for article in all_articles}
    
    bookmarked_articles = []
    for bookmark in bookmarks:
        article_id = bookmark.get("article_id")
        if article_id in article_dict:
            article_data = article_dict[article_id].copy()
            article_data["bookmarked_at"] = bookmark.get("bookmarked_at")
            bookmarked_articles.append(article_data)
    
    liked_articles = []
    for like in likes:
        article_id = like.get("article_id")
        if article_id in article_dict:
            article_data = article_dict[article_id].copy()
            article_data["liked_at"] = like.get("liked_at")
            liked_articles.append(article_data)
    
    return {
        "bookmarked": bookmarked_articles,
        "liked": liked_articles
    }

@router.get("/my-quiz-history")
async def get_my_quiz_history(current_user: User = Depends(get_current_active_user)):
    """Get user's quiz attempt history"""
    attempts = db.find_by_field("quiz_attempts", "user_id", current_user.id)
    
    # Get quiz details
    all_quizzes = db.read_all("quizzes")
    quiz_dict = {quiz["id"]: quiz for quiz in all_quizzes}
    
    # Enhance attempts with quiz details
    enhanced_attempts = []
    for attempt in attempts:
        quiz_id = attempt.get("quiz_id")
        if quiz_id in quiz_dict:
            attempt_data = attempt.copy()
            attempt_data["quiz"] = quiz_dict[quiz_id]
            enhanced_attempts.append(attempt_data)
    
    # Sort by attempt date (most recent first)
    enhanced_attempts.sort(key=lambda x: x.get("attempted_at", ""), reverse=True)
    
    return enhanced_attempts

@router.get("/search", response_model=SearchResults)
async def search_content(
    q: str = Query(..., description="Search query"),
    current_user: User = Depends(get_current_active_user)
):
    """Search across all content types"""
    search_term = q.lower()
    
    # Search courses
    courses = db.search("courses", search_term, ["title", "description", "category"])
    course_results = [Course(**course) for course in courses]
    
    # Search tutorials
    tutorials = db.search("tutorials", search_term, ["title", "description", "category"])
    tutorial_results = [Tutorial(**tutorial) for tutorial in tutorials]
    
    # Search articles
    articles = db.search("articles", search_term, ["title", "excerpt", "author", "tags"])
    article_results = [Article(**article) for article in articles]
    
    # Search quizzes
    quizzes = db.search("quizzes", search_term, ["title", "description", "category"])
    quiz_results = [Quiz(**quiz) for quiz in quizzes]
    
    return SearchResults(
        courses=course_results,
        tutorials=tutorial_results,
        articles=article_results,
        quizzes=quiz_results
    )

@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = Query(20, le=50),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's recent activity across all content types"""
    activities = []
    
    # Recent enrollments
    enrollments = db.find_by_field("enrollments", "user_id", current_user.id)
    for enrollment in enrollments[-5:]:  # Last 5 enrollments
        course = db.read("courses", enrollment.get("course_id"))
        if course:
            activities.append({
                "type": "enrollment",
                "action": "Enrolled in course",
                "title": course.get("title", "Unknown Course"),
                "date": enrollment.get("created_at"),
                "id": enrollment.get("course_id"),
                "entity_type": "course"
            })
    
    # Recent tutorial completions
    completions = db.find_by_field("completions", "user_id", current_user.id)
    for completion in completions[-5:]:  # Last 5 completions
        tutorial = db.read("tutorials", completion.get("tutorial_id"))
        if tutorial:
            activities.append({
                "type": "completion",
                "action": "Completed tutorial",
                "title": tutorial.get("title", "Unknown Tutorial"),
                "date": completion.get("completed_at"),
                "id": completion.get("tutorial_id"),
                "entity_type": "tutorial"
            })
    
    # Recent article bookmarks
    bookmarks = db.find_by_field("bookmarks", "user_id", current_user.id)
    for bookmark in bookmarks[-5:]:  # Last 5 bookmarks
        article = db.read("articles", bookmark.get("article_id"))
        if article:
            activities.append({
                "type": "bookmark",
                "action": "Bookmarked article",
                "title": article.get("title", "Unknown Article"),
                "date": bookmark.get("bookmarked_at"),
                "id": bookmark.get("article_id"),
                "entity_type": "article"
            })
    
    # Recent quiz attempts
    quiz_attempts = db.find_by_field("quiz_attempts", "user_id", current_user.id)
    for attempt in quiz_attempts[-5:]:  # Last 5 attempts
        quiz = db.read("quizzes", attempt.get("quiz_id"))
        if quiz:
            activities.append({
                "type": "quiz_attempt",
                "action": f"Attempted quiz (Score: {attempt.get('score', 0):.1f}%)",
                "title": quiz.get("title", "Unknown Quiz"),
                "date": attempt.get("attempted_at"),
                "id": attempt.get("quiz_id"),
                "entity_type": "quiz"
            })
    
    # Sort by date (most recent first)
    activities.sort(key=lambda x: x.get("date", ""), reverse=True)
    
    return activities[:limit]

@router.get("/recommendations")
async def get_recommendations(
    limit: int = Query(10, le=20),
    current_user: User = Depends(get_current_active_user)
):
    """Get personalized content recommendations"""
    # Get user's interests based on their activity
    enrollments = db.find_by_field("enrollments", "user_id", current_user.id)
    completions = db.find_by_field("completions", "user_id", current_user.id)
    quiz_attempts = db.find_by_field("quiz_attempts", "user_id", current_user.id)
    
    # Collect categories from user's activity
    user_categories = set()
    
    # From enrolled courses
    all_courses = db.read_all("courses")
    course_dict = {course["id"]: course for course in all_courses}
    for enrollment in enrollments:
        course_id = enrollment.get("course_id")
        if course_id in course_dict:
            user_categories.add(course_dict[course_id].get("category", "").lower())
    
    # From completed tutorials
    all_tutorials = db.read_all("tutorials")
    tutorial_dict = {tutorial["id"]: tutorial for tutorial in all_tutorials}
    for completion in completions:
        tutorial_id = completion.get("tutorial_id")
        if tutorial_id in tutorial_dict:
            user_categories.add(tutorial_dict[tutorial_id].get("category", "").lower())
    
    # From quiz attempts
    all_quizzes = db.read_all("quizzes")
    quiz_dict = {quiz["id"]: quiz for quiz in all_quizzes}
    for attempt in quiz_attempts:
        quiz_id = attempt.get("quiz_id")
        if quiz_id in quiz_dict:
            user_categories.add(quiz_dict[quiz_id].get("category", "").lower())
    
    recommendations = []
    
    # Recommend courses in user's interest categories
    enrolled_course_ids = set(e.get("course_id") for e in enrollments)
    for course in all_courses:
        if (course["id"] not in enrolled_course_ids and 
            course.get("category", "").lower() in user_categories):
            recommendations.append({
                "type": "course",
                "title": course.get("title"),
                "description": course.get("description"),
                "id": course["id"],
                "reason": f"Based on your interest in {course.get('category')}"
            })
    
    # Recommend tutorials in user's interest categories
    completed_tutorial_ids = set(c.get("tutorial_id") for c in completions)
    for tutorial in all_tutorials:
        if (tutorial["id"] not in completed_tutorial_ids and 
            tutorial.get("category", "").lower() in user_categories):
            recommendations.append({
                "type": "tutorial",
                "title": tutorial.get("title"),
                "description": tutorial.get("description"),
                "id": tutorial["id"],
                "reason": f"Based on your interest in {tutorial.get('category')}"
            })
    
    # Recommend quizzes in user's interest categories
    attempted_quiz_ids = set(a.get("quiz_id") for a in quiz_attempts)
    for quiz in all_quizzes:
        if (quiz["id"] not in attempted_quiz_ids and 
            quiz.get("category", "").lower() in user_categories):
            recommendations.append({
                "type": "quiz",
                "title": quiz.get("title"),
                "description": quiz.get("description"),
                "id": quiz["id"],
                "reason": f"Based on your interest in {quiz.get('category')}"
            })
    
    # If no specific interests, recommend popular content
    if not recommendations:
        # Most enrolled courses
        popular_courses = sorted(all_courses, key=lambda x: x.get("students", 0), reverse=True)[:3]
        for course in popular_courses:
            if course["id"] not in enrolled_course_ids:
                recommendations.append({
                    "type": "course",
                    "title": course.get("title"),
                    "description": course.get("description"),
                    "id": course["id"],
                    "reason": "Popular course"
                })
        
        # Most viewed tutorials
        popular_tutorials = sorted(all_tutorials, key=lambda x: x.get("views", 0), reverse=True)[:3]
        for tutorial in popular_tutorials:
            if tutorial["id"] not in completed_tutorial_ids:
                recommendations.append({
                    "type": "tutorial",
                    "title": tutorial.get("title"),
                    "description": tutorial.get("description"),
                    "id": tutorial["id"],
                    "reason": "Popular tutorial"
                })
    
    return recommendations[:limit] 