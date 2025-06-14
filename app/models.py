from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"
    RECRUITER = "recruiter"
    ADMIN = "admin"

class DifficultyLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"

# User Models
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.STUDENT
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    skills: List[str] = []
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Course Models
class CourseBase(BaseModel):
    title: str
    description: str
    duration: str
    price: str
    category: str
    level: DifficultyLevel
    image: str

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[str] = None
    price: Optional[str] = None
    category: Optional[str] = None
    level: Optional[DifficultyLevel] = None
    image: Optional[str] = None

class Course(CourseBase):
    id: int
    students: int = 0
    rating: float = 0.0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Tutorial Models
class TutorialBase(BaseModel):
    title: str
    description: str
    duration: str
    difficulty: DifficultyLevel
    image: str
    category: str
    level: DifficultyLevel

class TutorialCreate(TutorialBase):
    pass

class TutorialUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    image: Optional[str] = None
    category: Optional[str] = None
    level: Optional[DifficultyLevel] = None

class Tutorial(TutorialBase):
    id: int
    views: int = 0
    rating: float = 0.0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Article Models
class ArticleBase(BaseModel):
    title: str
    excerpt: str
    content: str
    author: str
    read_time: str
    image: str
    tags: List[str] = []

class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    read_time: Optional[str] = None
    image: Optional[str] = None
    tags: Optional[List[str]] = None

class Article(ArticleBase):
    id: int
    views: int = 0
    likes: int = 0
    published_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Quiz Models
class QuizQuestionOption(BaseModel):
    id: str
    text: str
    is_correct: bool = False

class QuizQuestion(BaseModel):
    id: int
    question: str
    options: List[QuizQuestionOption]
    explanation: Optional[str] = None

class QuizBase(BaseModel):
    title: str
    description: str
    questions_count: int
    difficulty: DifficultyLevel
    time_limit: str
    category: str

class QuizCreate(QuizBase):
    questions: List[QuizQuestion] = []

class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    questions_count: Optional[int] = None
    difficulty: Optional[DifficultyLevel] = None
    time_limit: Optional[str] = None
    category: Optional[str] = None
    questions: Optional[List[QuizQuestion]] = None

class Quiz(QuizBase):
    id: int
    questions: List[QuizQuestion] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# User Progress Models
class CourseEnrollment(BaseModel):
    id: int
    user_id: int
    course_id: int
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
    progress: float = 0.0

class TutorialCompletion(BaseModel):
    id: int
    user_id: int
    tutorial_id: int
    completed_at: datetime
    rating: Optional[float] = None

class ArticleBookmark(BaseModel):
    id: int
    user_id: int
    article_id: int
    bookmarked_at: datetime

class ArticleLike(BaseModel):
    id: int
    user_id: int
    article_id: int
    liked_at: datetime

class QuizAttempt(BaseModel):
    id: int
    user_id: int
    quiz_id: int
    score: float
    total_questions: int
    correct_answers: int
    attempted_at: datetime
    completed_at: Optional[datetime] = None
    answers: Dict[str, str] = {}

# Request/Response Models
class QuizSubmission(BaseModel):
    quiz_id: int
    answers: Dict[str, str]  # question_id -> selected_option_id

class QuizResult(BaseModel):
    quiz_id: int
    score: float
    total_questions: int
    correct_answers: int
    passed: bool
    answers: Dict[str, Dict[str, Any]]  # question_id -> result details

class DashboardStats(BaseModel):
    enrolled_courses: int
    completed_courses: int
    study_hours: int
    certificates: int
    completed_tutorials: int
    total_tutorials: int
    read_articles: int
    bookmarked_articles: int
    quiz_attempts: int
    average_quiz_score: float

class SearchResults(BaseModel):
    courses: List[Course] = []
    tutorials: List[Tutorial] = []
    articles: List[Article] = []
    quizzes: List[Quiz] = [] 