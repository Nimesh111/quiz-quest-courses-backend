from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from app.models import Quiz, QuizCreate, QuizUpdate, QuizAttempt, QuizSubmission, QuizResult, User
from app.database import db
from app.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[Quiz])
async def get_quizzes(
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty level"),
    search: Optional[str] = Query(None, description="Search in title and description")
):
    """Get all quizzes with optional filtering"""
    quizzes = db.read_all("quizzes")
    
    # Convert to Quiz objects
    quiz_list = [Quiz(**quiz) for quiz in quizzes]
    
    # Apply filters
    if category:
        quiz_list = [q for q in quiz_list if q.category.lower() == category.lower()]
    
    if difficulty:
        quiz_list = [q for q in quiz_list if q.difficulty.lower() == difficulty.lower()]
    
    if search:
        search_term = search.lower()
        quiz_list = [
            q for q in quiz_list 
            if search_term in q.title.lower() or search_term in q.description.lower()
        ]
    
    return quiz_list

@router.get("/{quiz_id}", response_model=Quiz)
async def get_quiz(quiz_id: int, include_answers: bool = Query(False)):
    """Get quiz by ID"""
    quiz = db.read("quizzes", quiz_id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Remove correct answers from questions if not requested
    if not include_answers:
        for question in quiz.get("questions", []):
            for option in question.get("options", []):
                option.pop("is_correct", None)
    
    return Quiz(**quiz)

@router.post("/", response_model=Quiz, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    quiz: QuizCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new quiz (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    quiz_data = quiz.dict()
    created_quiz = db.create("quizzes", quiz_data)
    
    return Quiz(**created_quiz)

@router.put("/{quiz_id}", response_model=Quiz)
async def update_quiz(
    quiz_id: int,
    quiz_update: QuizUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update a quiz (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    existing_quiz = db.read("quizzes", quiz_id)
    if not existing_quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    update_data = quiz_update.dict(exclude_unset=True)
    updated_quiz = db.update("quizzes", quiz_id, update_data)
    
    return Quiz(**updated_quiz)

@router.delete("/{quiz_id}")
async def delete_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a quiz (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = db.delete("quizzes", quiz_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    return {"message": "Quiz deleted successfully"}

@router.post("/{quiz_id}/attempt", response_model=QuizResult)
async def submit_quiz(
    quiz_id: int,
    submission: QuizSubmission,
    current_user: User = Depends(get_current_active_user)
):
    """Submit quiz answers and get results"""
    # Check if quiz exists
    quiz = db.read("quizzes", quiz_id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Validate submission
    if submission.quiz_id != quiz_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz ID mismatch"
        )
    
    # Calculate score
    questions = quiz.get("questions", [])
    total_questions = len(questions)
    correct_answers = 0
    answer_details = {}
    
    for question in questions:
        question_id = str(question["id"])
        user_answer = submission.answers.get(question_id)
        
        # Find correct answer
        correct_option = None
        for option in question.get("options", []):
            if option.get("is_correct", False):
                correct_option = option["id"]
                break
        
        is_correct = user_answer == correct_option
        if is_correct:
            correct_answers += 1
        
        answer_details[question_id] = {
            "question": question["question"],
            "user_answer": user_answer,
            "correct_answer": correct_option,
            "is_correct": is_correct,
            "explanation": question.get("explanation", "")
        }
    
    # Calculate percentage score
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    passed = score >= 60  # 60% passing score
    
    # Save attempt
    attempt_data = {
        "user_id": current_user.id,
        "quiz_id": quiz_id,
        "score": score,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "answers": submission.answers
    }
    
    from datetime import datetime
    attempt_data["completed_at"] = datetime.now().isoformat()
    
    db.create("quiz_attempts", attempt_data)
    
    return QuizResult(
        quiz_id=quiz_id,
        score=score,
        total_questions=total_questions,
        correct_answers=correct_answers,
        passed=passed,
        answers=answer_details
    )

@router.get("/{quiz_id}/attempts")
async def get_quiz_attempts(
    quiz_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Get user's quiz attempts"""
    attempts = db.find_by_field("quiz_attempts", "user_id", current_user.id)
    quiz_attempts = [a for a in attempts if a.get("quiz_id") == quiz_id]
    
    return quiz_attempts

@router.get("/{quiz_id}/best-score")
async def get_best_score(
    quiz_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Get user's best score for a quiz"""
    attempts = db.find_by_field("quiz_attempts", "user_id", current_user.id)
    quiz_attempts = [a for a in attempts if a.get("quiz_id") == quiz_id]
    
    if not quiz_attempts:
        return {"best_score": None, "attempts": 0}
    
    best_score = max(attempt.get("score", 0) for attempt in quiz_attempts)
    
    return {
        "best_score": best_score,
        "attempts": len(quiz_attempts),
        "passed": best_score >= 60
    }

@router.get("/{quiz_id}/leaderboard")
async def get_quiz_leaderboard(quiz_id: int, limit: int = Query(10, le=50)):
    """Get quiz leaderboard"""
    # Get all attempts for this quiz
    all_attempts = db.read_all("quiz_attempts")
    quiz_attempts = [a for a in all_attempts if a.get("quiz_id") == quiz_id]
    
    # Group by user and get best score
    user_best_scores = {}
    for attempt in quiz_attempts:
        user_id = attempt.get("user_id")
        score = attempt.get("score", 0)
        
        if user_id not in user_best_scores or score > user_best_scores[user_id]["score"]:
            user_best_scores[user_id] = {
                "user_id": user_id,
                "score": score,
                "correct_answers": attempt.get("correct_answers", 0),
                "total_questions": attempt.get("total_questions", 0),
                "attempted_at": attempt.get("attempted_at", "")
            }
    
    # Sort by score descending
    leaderboard = sorted(user_best_scores.values(), key=lambda x: x["score"], reverse=True)
    
    # Add user information
    users = db.read_all("users")
    user_dict = {user["id"]: user for user in users}
    
    for entry in leaderboard:
        user_id = entry["user_id"]
        if user_id in user_dict:
            entry["username"] = user_dict[user_id].get("username", "Unknown")
            entry["full_name"] = user_dict[user_id].get("full_name", "")
        else:
            entry["username"] = "Unknown"
            entry["full_name"] = ""
    
    return leaderboard[:limit]

@router.get("/categories")
async def get_quiz_categories():
    """Get all quiz categories"""
    quizzes = db.read_all("quizzes")
    categories = list(set(quiz.get("category", "") for quiz in quizzes if quiz.get("category")))
    return sorted(categories)

@router.get("/stats")
async def get_quiz_stats(current_user: User = Depends(get_current_active_user)):
    """Get user's quiz statistics"""
    attempts = db.find_by_field("quiz_attempts", "user_id", current_user.id)
    
    if not attempts:
        return {
            "total_attempts": 0,
            "quizzes_attempted": 0,
            "average_score": 0,
            "passed_quizzes": 0,
            "best_category": None
        }
    
    # Calculate stats
    total_attempts = len(attempts)
    unique_quizzes = len(set(a.get("quiz_id") for a in attempts))
    average_score = sum(a.get("score", 0) for a in attempts) / total_attempts
    passed_attempts = len([a for a in attempts if a.get("score", 0) >= 60])
    
    # Find best category
    quizzes = db.read_all("quizzes")
    quiz_dict = {q["id"]: q for q in quizzes}
    
    category_scores = {}
    for attempt in attempts:
        quiz_id = attempt.get("quiz_id")
        if quiz_id in quiz_dict:
            category = quiz_dict[quiz_id].get("category", "")
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(attempt.get("score", 0))
    
    best_category = None
    best_avg = 0
    for category, scores in category_scores.items():
        avg = sum(scores) / len(scores)
        if avg > best_avg:
            best_avg = avg
            best_category = category
    
    return {
        "total_attempts": total_attempts,
        "quizzes_attempted": unique_quizzes,
        "average_score": round(average_score, 2),
        "passed_quizzes": passed_attempts,
        "best_category": best_category
    } 