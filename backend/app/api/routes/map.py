"""Map Service API Routes"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ...models.schemas import (
    POISearchRequest,
    POISearchResponse,
    RouteRequest,
    RouteResponse,
    WeatherResponse
)
from ...services.amap_service import get_amap_service

router = APIRouter(prefix="/map", tags=["Map Service"])


@router.get(
    "/poi",
    response_model=POISearchResponse,
    summary="Search POI",
    description="Search for POIs (Points of Interest) by keywords"
)
async def search_poi(
    keywords: str = Query(..., description="Search keywords", example="Forbidden City"),
    city: str = Query(..., description="City name", example="Beijing"),
    citylimit: bool = Query(True, description="Whether to limit search within city boundaries")
):
    """
    Search POI
    
    Args:
        keywords: Search keywords
        city: City name
        citylimit: Whether to limit search within city boundaries
        
    Returns:
        POI search results
    """
    try:
        # Get service instance
        service = get_amap_service()
        
        # Search POI
        pois = service.search_poi(keywords, city, citylimit)
        
        return POISearchResponse(
            success=True,
            message="POI search successful",
            data=pois
        )
        
    except Exception as e:
        print(f"❌ POI search failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"POI search failed: {str(e)}"
        )


@router.get(
    "/weather",
    response_model=WeatherResponse,
    summary="Query Weather",
    description="Query weather information for a specified city"
)
async def get_weather(
    city: str = Query(..., description="City name", example="Beijing")
):
    """
    Query weather
    
    Args:
        city: City name
        
    Returns:
        Weather information
    """
    try:
        # Get service instance
        service = get_amap_service()
        
        # Query weather
        weather_info = service.get_weather(city)
        
        return WeatherResponse(
            success=True,
            message="Weather query successful",
            data=weather_info
        )
        
    except Exception as e:
        print(f"❌ Weather query failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Weather query failed: {str(e)}"
        )


@router.post(
    "/route",
    response_model=RouteResponse,
    summary="Plan Route",
    description="Plan a route between two points"
)
async def plan_route(request: RouteRequest):
    """
    Plan route
    
    Args:
        request: Route planning request
        
    Returns:
        Route information
    """
    try:
        # Get service instance
        service = get_amap_service()
        
        # Plan route
        route_info = service.plan_route(
            origin_address=request.origin_address,
            destination_address=request.destination_address,
            origin_city=request.origin_city,
            destination_city=request.destination_city,
            route_type=request.route_type
        )
        
        return RouteResponse(
            success=True,
            message="Route planning successful",
            data=route_info
        )
        
    except Exception as e:
        print(f"❌ Route planning failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Route planning failed: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health Check",
    description="Check if the map service is running normally"
)
async def health_check():
    """Health check"""
    try:
        # Check if service is available
        service = get_amap_service()
        
        return {
            "status": "healthy",
            "service": "map-service",
            "mcp_tools_count": len(service.mcp_tool._available_tools)
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

