"""POI Related API Routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from ...services.amap_service import get_amap_service
from ...services.unsplash_service import get_unsplash_service

router = APIRouter(prefix="/poi", tags=["POI"])


class POIDetailResponse(BaseModel):
    """POI详情响应"""
    success: bool
    message: str
    data: Optional[dict] = None


@router.get(
    "/detail/{poi_id}",
    response_model=POIDetailResponse,
    summary="Get POI Details",
    description="Get detailed information for a POI by ID, including images"
)
async def get_poi_detail(poi_id: str):
    """
    Get POI details
    
    Args:
        poi_id: POI ID
        
    Returns:
        POI details response
    """
    try:
        amap_service = get_amap_service()
        
        # Call Amap POI details API
        result = amap_service.get_poi_detail(poi_id)
        
        return POIDetailResponse(
            success=True,
            message="POI details retrieved successfully",
            data=result
        )
        
    except Exception as e:
        print(f"❌ Failed to get POI details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get POI details: {str(e)}"
        )


@router.get(
    "/search",
    summary="Search POI",
    description="Search for POIs by keywords"
)
async def search_poi(keywords: str, city: str = "Beijing"):
    """
    Search POI

    Args:
        keywords: Search keywords
        city: City name

    Returns:
        Search results
    """
    try:
        amap_service = get_amap_service()
        result = amap_service.search_poi(keywords, city)

        return {
            "success": True,
            "message": "Search successful",
            "data": result
        }

    except Exception as e:
        print(f"❌ POI search failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"POI search failed: {str(e)}"
        )


@router.get(
    "/photo",
    summary="Get Attraction Photo",
    description="Get photo for an attraction by name from Unsplash"
)
async def get_attraction_photo(name: str):
    """
    Get attraction photo

    Args:
        name: Attraction name

    Returns:
        Photo URL
    """
    try:
        unsplash_service = get_unsplash_service()

        # Search for attraction photo
        photo_url = unsplash_service.get_photo_url(f"{name} China landmark")

        if not photo_url:
            # If not found, try searching with just the attraction name
            photo_url = unsplash_service.get_photo_url(name)

        return {
            "success": True,
            "message": "Photo retrieved successfully",
            "data": {
                "name": name,
                "photo_url": photo_url
            }
        }

    except Exception as e:
        print(f"❌ Failed to get attraction photo: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get attraction photo: {str(e)}"
        )

