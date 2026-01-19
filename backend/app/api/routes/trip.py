"""Trip Planning API Routes"""

from fastapi import APIRouter, HTTPException
from ...models.schemas import (
    TripRequest,
    TripPlanResponse,
    ErrorResponse
)
from ...agents.trip_planner_agent import get_trip_planner_agent

router = APIRouter(prefix="/trip", tags=["Trip Planning"])


@router.post(
    "/plan",
    response_model=TripPlanResponse,
    summary="Generate Trip Plan",
    description="Generate a detailed trip plan based on user's travel requirements"
)
async def plan_trip(request: TripRequest):
    """
    Generate trip plan

    Args:
        request: Trip request parameters

    Returns:
        Trip plan response
    """
    try:
        print(f"\n{'='*60}")
        print(f"📥 Received trip planning request:")
        print(f"   City: {request.city}")
        print(f"   Dates: {request.start_date} - {request.end_date}")
        print(f"   Days: {request.travel_days}")
        print(f"{'='*60}\n")

        # Get Agent instance
        print("🔄 Getting multi-agent system instance...")
        agent = get_trip_planner_agent()

        # Generate trip plan
        print("🚀 Starting trip plan generation...")
        trip_plan = agent.plan_trip(request)

        print("✅ Trip plan generated successfully, preparing response")
        
        # Debug: Print basic information of trip_plan
        print(f"🔍 Debug information:")
        print(f"   trip_plan type: {type(trip_plan)}")
        print(f"   city: {trip_plan.city}")
        print(f"   days count: {len(trip_plan.days)}")
        print(f"   weather_info count: {len(trip_plan.weather_info)}")
        print(f"   overall_suggestions length: {len(trip_plan.overall_suggestions)}")
        print(f"   budget: {trip_plan.budget}")
        
        # Debug: Check completeness of days
        for i, day in enumerate(trip_plan.days):
            print(f"   Day {i}: attractions={len(day.attractions)}, meals={len(day.meals)}, hotel={day.hotel is not None}")
        
        # Debug: Convert to JSON for checking
        try:
            import json
            response_data = TripPlanResponse(
                success=True,
                message="Trip plan generated successfully",
                data=trip_plan
            )
            json_str = json.dumps(response_data.model_dump(), ensure_ascii=False, indent=2)
            print(f"   JSON length: {len(json_str)} characters")
            print(f"   JSON first 500 characters: {json_str[:500]}...")
        except Exception as e:
            print(f"   ⚠️ JSON serialization failed: {str(e)}")
        
        print()

        return TripPlanResponse(
            success=True,
            message="Trip plan generated successfully",
            data=trip_plan
        )

    except Exception as e:
        print(f"❌ Trip plan generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate trip plan: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health Check",
    description="Check if the trip planning service is running normally"
)
async def health_check():
    """Health check"""
    try:
        # Check if Agent is available
        agent = get_trip_planner_agent()
        
        return {
            "status": "healthy",
            "service": "trip-planner",
            "agent_name": agent.attraction_agent.name,
            "tools_count": len(agent.amap_tools)
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

