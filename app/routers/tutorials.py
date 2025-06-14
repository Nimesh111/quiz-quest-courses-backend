from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from app.models import Tutorial, TutorialCreate, TutorialUpdate, TutorialCompletion, User
from app.database import db
from app.auth import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[Tutorial])
async def get_tutorials(
    category: Optional[str] = Query(None, description="Filter by category"),
    level: Optional[str] = Query(None, description="Filter by difficulty level"),
    search: Optional[str] = Query(None, description="Search in title and description")
):
    """Get all tutorials with optional filtering"""
    tutorials = db.read_all("tutorials")
    
    # Convert to Tutorial objects
    tutorial_list = [Tutorial(**tutorial) for tutorial in tutorials]
    
    # Apply filters
    if category:
        tutorial_list = [t for t in tutorial_list if t.category.lower() == category.lower()]
    
    if level:
        tutorial_list = [t for t in tutorial_list if t.level.lower() == level.lower()]
    
    if search:
        search_term = search.lower()
        tutorial_list = [
            t for t in tutorial_list 
            if search_term in t.title.lower() or search_term in t.description.lower()
        ]
    
    return tutorial_list

@router.get("/{tutorial_id}", response_model=Tutorial)
async def get_tutorial(tutorial_id: int):
    """Get tutorial by ID"""
    tutorial = db.read("tutorials", tutorial_id)
    if not tutorial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutorial not found"
        )
    
    # Increment view count
    current_views = tutorial.get("views", 0)
    db.update("tutorials", tutorial_id, {"views": current_views + 1})
    tutorial["views"] = current_views + 1
    
    return Tutorial(**tutorial)

@router.post("/", response_model=Tutorial, status_code=status.HTTP_201_CREATED)
async def create_tutorial(
    tutorial: TutorialCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new tutorial (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    tutorial_data = tutorial.dict()
    created_tutorial = db.create("tutorials", tutorial_data)
    
    return Tutorial(**created_tutorial)

@router.put("/{tutorial_id}", response_model=Tutorial)
async def update_tutorial(
    tutorial_id: int,
    tutorial_update: TutorialUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update a tutorial (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    existing_tutorial = db.read("tutorials", tutorial_id)
    if not existing_tutorial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutorial not found"
        )
    
    update_data = tutorial_update.dict(exclude_unset=True)
    updated_tutorial = db.update("tutorials", tutorial_id, update_data)
    
    return Tutorial(**updated_tutorial)

@router.delete("/{tutorial_id}")
async def delete_tutorial(
    tutorial_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a tutorial (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = db.delete("tutorials", tutorial_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutorial not found"
        )
    
    return {"message": "Tutorial deleted successfully"}

@router.post("/{tutorial_id}/complete", response_model=TutorialCompletion)
async def complete_tutorial(
    tutorial_id: int,
    rating: Optional[float] = Query(None, description="Rating for the tutorial (1-5)"),
    current_user: User = Depends(get_current_active_user)
):
    """Mark tutorial as completed"""
    # Check if tutorial exists
    tutorial = db.read("tutorials", tutorial_id)
    if not tutorial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutorial not found"
        )
    
    # Check if already completed
    completions = db.find_by_field("completions", "user_id", current_user.id)
    existing_completion = next((c for c in completions if c.get("tutorial_id") == tutorial_id), None)
    if existing_completion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tutorial already completed"
        )
    
    # Validate rating
    if rating is not None and (rating < 1 or rating > 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    # Create completion record
    completion_data = {
        "user_id": current_user.id,
        "tutorial_id": tutorial_id,
        "rating": rating
    }
    
    completion = db.create("completions", completion_data)
    
    return TutorialCompletion(**completion)

@router.get("/{tutorial_id}/completed")
async def check_completion(
    tutorial_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Check if user has completed a tutorial"""
    completions = db.find_by_field("completions", "user_id", current_user.id)
    completed = any(c.get("tutorial_id") == tutorial_id for c in completions)
    
    return {"completed": completed}

@router.delete("/{tutorial_id}/complete")
async def uncomplete_tutorial(
    tutorial_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Remove tutorial completion"""
    # Find completion
    completions = db.find_by_field("completions", "user_id", current_user.id)
    completion = next((c for c in completions if c.get("tutorial_id") == tutorial_id), None)
    
    if not completion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutorial completion not found"
        )
    
    # Delete completion
    db.delete("completions", completion["id"])
    
    return {"message": "Tutorial completion removed successfully"} 