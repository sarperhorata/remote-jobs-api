from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Optional
from models.models import Website, WebsiteCreate, WebsiteType, SelectorBase
from utils.db import get_websites, get_website, create_website, update_website, delete_website

router = APIRouter()

@router.get("/", response_model=List[Website])
async def get_all_websites(
    website_type: Optional[WebsiteType] = Query(None, description="Filter by website type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    include_inactive: bool = Query(False, description="Include inactive websites")
):
    """
    Lists all websites
    """
    websites = await get_websites(include_inactive=include_inactive)
    
    # Filtering operations
    if website_type:
        websites = [w for w in websites if w.website_type == website_type]
    
    if is_active is not None:
        websites = [w for w in websites if w.is_active == is_active]
    
    return websites

@router.get("/{website_id}", response_model=Website)
async def get_website_by_id(website_id: int):
    """
    Gets a specific website by ID
    """
    website = await get_website(website_id)
    if not website:
        raise HTTPException(status_code=404, detail=f"Website with ID {website_id} not found")
    return website

@router.post("/", response_model=Website)
async def create_new_website(website: WebsiteCreate):
    """
    Creates a new website
    """
    # Convert schema to dictionary (exclude_unset=True ensures None values are not sent)
    website_data = website.dict(exclude_unset=True)
    
    # Save to database
    website_id = await create_website(website_data)
    
    if not website_id:
        raise HTTPException(status_code=400, detail="Could not create website")
    
    # Return the created website
    return await get_website(website_id)

@router.put("/{website_id}", response_model=Website)
async def update_existing_website(website_id: int, website_update: WebsiteCreate):
    """
    Updates an existing website
    """
    # First check if the website exists
    existing_website = await get_website(website_id)
    if not existing_website:
        raise HTTPException(status_code=404, detail=f"Website with ID {website_id} not found")
    
    # Convert schema to dictionary (exclude_unset=True ensures None values are not sent)
    website_data = website_update.dict(exclude_unset=True)
    
    # Update in database
    success = await update_website(website_id, website_data)
    
    if not success:
        raise HTTPException(status_code=400, detail="Website update failed")
    
    # Return the updated website
    return await get_website(website_id)

@router.delete("/{website_id}")
async def delete_existing_website(website_id: int):
    """
    Deletes a website
    """
    # First check if the website exists
    existing_website = await get_website(website_id)
    if not existing_website:
        raise HTTPException(status_code=404, detail=f"Website with ID {website_id} not found")
    
    # Delete from database
    success = await delete_website(website_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Website deletion failed")
    
    return {"message": f"Website with ID {website_id} successfully deleted"}

@router.get("/types", response_model=List[str])
async def get_website_types():
    """
    Lists supported website types
    """
    return [t.value for t in WebsiteType]

@router.post("/{website_id}/add_selector", response_model=Website)
async def add_selector_to_website(website_id: int, selector: SelectorBase):
    """
    Adds a selector to a website
    """
    # First check if the website exists
    website = await get_website(website_id)
    if not website:
        raise HTTPException(status_code=404, detail=f"Website with ID {website_id} not found")
    
    # Add the selector
    selectors = website.selectors if website.selectors else []
    selectors.append(selector)
    
    # Update the website
    success = await update_website(website_id, {"selectors": selectors})
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add selector")
    
    # Return the updated website
    return await get_website(website_id)

@router.delete("/{website_id}/remove_selector/{selector_name}")
async def remove_selector_from_website(website_id: int, selector_name: str):
    """
    Removes a specific selector from a website
    """
    # First check if the website exists
    website = await get_website(website_id)
    if not website:
        raise HTTPException(status_code=404, detail=f"Website with ID {website_id} not found")
    
    # Check if the selector exists
    selectors = website.selectors if website.selectors else []
    original_count = len(selectors)
    selectors = [s for s in selectors if s.name != selector_name]
    
    if len(selectors) == original_count:
        raise HTTPException(status_code=404, detail=f"Selector with name '{selector_name}' not found")
    
    # Update the website
    success = await update_website(website_id, {"selectors": selectors})
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to remove selector")
    
    return {"message": f"Selector '{selector_name}' removed from website ID {website_id}"} 