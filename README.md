# Quiz Quest Backend API

A comprehensive FastAPI backend for the Quiz Quest educational platform with course management, tutorials, articles, quizzes, and user authentication.

## 🚀 Quick Start

### Setup & Run
```bash
# 1. Setup (creates venv and installs dependencies)
./setup.sh

# 2. Start server (activates venv and runs server)
python start_server.py
```

### Manual Setup
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python start_server.py
```

## 📚 API Access

Once running:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## 🔑 Test Users

```
Admin: admin@example.com / admin123
Student: john.doe@example.com / password123
```

## 🏗️ Project Structure

```
quiz-quest-courses-backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── models.py            # Data models
│   ├── database.py          # JSON database
│   ├── auth.py              # Authentication
│   └── routers/             # API endpoints
├── data/                    # JSON data storage
├── requirements.txt         # Dependencies
├── setup.sh                 # Setup script
├── start_server.py          # Server launcher
└── seed_data.py             # Sample data
```

## 🛠️ Key API Endpoints

### Authentication
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login (form data)
- `POST /api/auth/login-json` - Login (JSON)

### Courses
- `GET /api/courses` - List courses
- `POST /api/courses/{id}/enroll` - Enroll in course
- `PUT /api/courses/{id}/progress` - Update progress

### Tutorials
- `GET /api/tutorials` - List tutorials
- `POST /api/tutorials/{id}/complete` - Mark complete

### Articles
- `GET /api/articles` - List articles
- `POST /api/articles/{id}/bookmark` - Bookmark
- `POST /api/articles/{id}/like` - Like article

### Quizzes
- `GET /api/quizzes` - List quizzes
- `POST /api/quizzes/{id}/submit` - Submit answers
- `GET /api/quizzes/{id}/leaderboard` - View scores

### Dashboard
- `GET /api/dashboard/stats` - User statistics
- `GET /api/dashboard/search` - Global search

## 💾 Features

- ✅ JWT Authentication with role-based access
- ✅ Course enrollment and progress tracking
- ✅ Tutorial completion system
- ✅ Article bookmarking and likes
- ✅ Interactive quiz engine with scoring
- ✅ Dashboard analytics
- ✅ JSON file-based storage (no database required)
- ✅ Automatic sample data seeding
- ✅ CORS enabled for frontend integration

## 🔧 Development

```bash
# To stop server
Ctrl+C

# To restart
python start_server.py

# View logs
Check terminal output
```

---

🎯 **Ready for your React frontend integration!** # quiz-quest-courses-backend
