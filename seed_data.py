#!/usr/bin/env python3
"""
Data seeding script for Quiz Quest Courses API
This script populates the database with sample data matching the frontend requirements
"""

import json
import os
from datetime import datetime, timedelta
from app.database import db
from app.auth import get_password_hash

def seed_users():
    """Seed sample users"""
    users = [
        {
            "email": "admin@example.com",
            "username": "admin",
            "full_name": "System Administrator",
            "role": "admin",
            "password": get_password_hash("admin123"),
            "avatar_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
            "bio": "System administrator",
            "skills": ["Admin", "Management"]
        },
        {
            "email": "john.doe@example.com",
            "username": "johndoe",
            "full_name": "John Doe",
            "role": "student",
            "password": get_password_hash("password123"),
            "avatar_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face",
            "bio": "Web developer",
            "skills": ["JavaScript", "Python", "React"]
        }
    ]
    
    print("Seeding users...")
    for user_data in users:
        existing = db.find_one_by_field("users", "email", user_data["email"])
        if not existing:
            db.create("users", user_data)
            print(f"Created user: {user_data['username']}")

def seed_courses():
    """Seed sample courses"""
    courses = [
        {
            "title": "Introduction to Web Development",
            "description": "Learn HTML, CSS, and JavaScript from scratch with hands-on projects.",
            "duration": "12 weeks",
            "price": "$99",
            "category": "Programming",
            "level": "Beginner",
            "image": "https://images.unsplash.com/photo-1517077304055-6e89abbf09b0?w=400&h=250&fit=crop",
            "students": 1250,
            "rating": 4.8
        },
        {
            "title": "Data Science Fundamentals",
            "description": "Master Python, statistics, and machine learning for data analysis.",
            "duration": "16 weeks",
            "price": "$149",
            "category": "Data Science",
            "level": "Intermediate",
            "image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=250&fit=crop",
            "students": 890,
            "rating": 4.9
        }
    ]
    
    print("Seeding courses...")
    for course_data in courses:
        existing = db.find_one_by_field("courses", "title", course_data["title"])
        if not existing:
            db.create("courses", course_data)
            print(f"Created course: {course_data['title']}")

def seed_tutorials():
    """Seed sample tutorials"""
    tutorials = [
        {
            "title": "Getting Started with React",
            "description": "Learn the basics of React and component-based development.",
            "duration": "30 min",
            "difficulty": "Beginner",
            "image": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=400&h=250&fit=crop",
            "category": "Programming",
            "level": "Beginner",
            "views": 15420,
            "rating": 4.7
        }
    ]
    
    print("Seeding tutorials...")
    for tutorial_data in tutorials:
        existing = db.find_one_by_field("tutorials", "title", tutorial_data["title"])
        if not existing:
            db.create("tutorials", tutorial_data)
            print(f"Created tutorial: {tutorial_data['title']}")

def seed_articles():
    """Seed sample articles"""
    articles = [
        {
            "title": "10 Web Development Trends in 2024",
            "excerpt": "Discover the latest trends shaping the future of web development.",
            "content": "The web development landscape is constantly evolving...",
            "author": "John Smith",
            "read_time": "5 min read",
            "image": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=250&fit=crop",
            "tags": ["Web Development", "Trends", "Technology"],
            "views": 2580,
            "likes": 154,
            "published_date": datetime.now().isoformat()
        }
    ]
    
    print("Seeding articles...")
    for article_data in articles:
        existing = db.find_one_by_field("articles", "title", article_data["title"])
        if not existing:
            db.create("articles", article_data)
            print(f"Created article: {article_data['title']}")

def seed_quizzes():
    """Seed sample quizzes"""
    quizzes = [
        {
            "title": "HTML Fundamentals Quiz",
            "description": "Test your knowledge of HTML basics.",
            "questions_count": 2,
            "difficulty": "Beginner",
            "time_limit": "20 min",
            "category": "Web Development",
            "questions": [
                {
                    "id": 1,
                    "question": "What does HTML stand for?",
                    "options": [
                        {"id": "a", "text": "HyperText Markup Language", "is_correct": True},
                        {"id": "b", "text": "High-Level Text Language", "is_correct": False}
                    ],
                    "explanation": "HTML stands for HyperText Markup Language."
                }
            ]
        }
    ]
    
    print("Seeding quizzes...")
    for quiz_data in quizzes:
        existing = db.find_one_by_field("quizzes", "title", quiz_data["title"])
        if not existing:
            db.create("quizzes", quiz_data)
            print(f"Created quiz: {quiz_data['title']}")

def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")
    seed_users()
    seed_courses()
    seed_tutorials()
    seed_articles()
    seed_quizzes()
    print("✅ Database seeding completed!")
    print("Login: admin@example.com / admin123")
    print("Login: john.doe@example.com / password123")

if __name__ == "__main__":
    main() 