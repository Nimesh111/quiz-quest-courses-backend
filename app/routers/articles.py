from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from app.models import Article, ArticleCreate, ArticleUpdate, ArticleBookmark, ArticleLike, User
from app.database import db
from app.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[Article])
async def get_articles(
    search: Optional[str] = Query(None, description="Search in title, excerpt, and tags"),
    author: Optional[str] = Query(None, description="Filter by author"),
    tag: Optional[str] = Query(None, description="Filter by tag")
):
    """Get all articles with optional filtering"""
    articles = db.read_all("articles")
    
    # Convert to Article objects
    article_list = [Article(**article) for article in articles]
    
    # Apply filters
    if search:
        search_term = search.lower()
        article_list = [
            a for a in article_list 
            if search_term in a.title.lower() or 
               search_term in a.excerpt.lower() or
               any(search_term in tag.lower() for tag in a.tags)
        ]
    
    if author:
        article_list = [a for a in article_list if a.author.lower() == author.lower()]
    
    if tag:
        article_list = [a for a in article_list if tag.lower() in [t.lower() for t in a.tags]]
    
    return article_list

@router.get("/{article_id}", response_model=Article)
async def get_article(article_id: int):
    """Get article by ID"""
    article = db.read("articles", article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Increment view count
    current_views = article.get("views", 0)
    db.update("articles", article_id, {"views": current_views + 1})
    article["views"] = current_views + 1
    
    return Article(**article)

@router.post("/", response_model=Article, status_code=status.HTTP_201_CREATED)
async def create_article(
    article: ArticleCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new article (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    article_data = article.dict()
    from datetime import datetime
    article_data["published_date"] = datetime.now().isoformat()
    
    created_article = db.create("articles", article_data)
    
    return Article(**created_article)

@router.put("/{article_id}", response_model=Article)
async def update_article(
    article_id: int,
    article_update: ArticleUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update an article (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    existing_article = db.read("articles", article_id)
    if not existing_article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    update_data = article_update.dict(exclude_unset=True)
    updated_article = db.update("articles", article_id, update_data)
    
    return Article(**updated_article)

@router.delete("/{article_id}")
async def delete_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Delete an article (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = db.delete("articles", article_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    return {"message": "Article deleted successfully"}

@router.post("/{article_id}/bookmark", response_model=ArticleBookmark)
async def bookmark_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Bookmark an article"""
    # Check if article exists
    article = db.read("articles", article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Check if already bookmarked
    bookmarks = db.find_by_field("bookmarks", "user_id", current_user.id)
    existing_bookmark = next((b for b in bookmarks if b.get("article_id") == article_id), None)
    if existing_bookmark:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article already bookmarked"
        )
    
    # Create bookmark
    bookmark_data = {
        "user_id": current_user.id,
        "article_id": article_id
    }
    
    bookmark = db.create("bookmarks", bookmark_data)
    
    return ArticleBookmark(**bookmark)

@router.delete("/{article_id}/bookmark")
async def remove_bookmark(
    article_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Remove article bookmark"""
    # Find bookmark
    bookmarks = db.find_by_field("bookmarks", "user_id", current_user.id)
    bookmark = next((b for b in bookmarks if b.get("article_id") == article_id), None)
    
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )
    
    # Delete bookmark
    db.delete("bookmarks", bookmark["id"])
    
    return {"message": "Bookmark removed successfully"}

@router.get("/{article_id}/bookmarked")
async def check_bookmark(
    article_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Check if user has bookmarked an article"""
    bookmarks = db.find_by_field("bookmarks", "user_id", current_user.id)
    bookmarked = any(b.get("article_id") == article_id for b in bookmarks)
    
    return {"bookmarked": bookmarked}

@router.post("/{article_id}/like", response_model=ArticleLike)
async def like_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Like an article"""
    # Check if article exists
    article = db.read("articles", article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Check if already liked
    likes = db.find_by_field("likes", "user_id", current_user.id)
    existing_like = next((l for l in likes if l.get("article_id") == article_id), None)
    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article already liked"
        )
    
    # Create like
    like_data = {
        "user_id": current_user.id,
        "article_id": article_id
    }
    
    like = db.create("likes", like_data)
    
    # Update article like count
    current_likes = article.get("likes", 0)
    db.update("articles", article_id, {"likes": current_likes + 1})
    
    return ArticleLike(**like)

@router.delete("/{article_id}/like")
async def unlike_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Remove article like"""
    # Find like
    likes = db.find_by_field("likes", "user_id", current_user.id)
    like = next((l for l in likes if l.get("article_id") == article_id), None)
    
    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found"
        )
    
    # Delete like
    db.delete("likes", like["id"])
    
    # Update article like count
    article = db.read("articles", article_id)
    if article:
        current_likes = max(0, article.get("likes", 1) - 1)
        db.update("articles", article_id, {"likes": current_likes})
    
    return {"message": "Like removed successfully"}

@router.get("/{article_id}/liked")
async def check_like(
    article_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Check if user has liked an article"""
    likes = db.find_by_field("likes", "user_id", current_user.id)
    liked = any(l.get("article_id") == article_id for l in likes)
    
    return {"liked": liked} 