"""旅行规划API路由"""

from fastapi import APIRouter, HTTPException
from ...models.schemas import (
    TripRequest,
    TripPlanResponse,
    ErrorResponse
)
from ...agents.trip_planner_agent import get_trip_planner_agent

router = APIRouter(prefix="/trip", tags=["旅行规划"])


@router.post(
    "/plan",
    response_model=TripPlanResponse,
    summary="生成旅行计划",
    description="根据用户输入的旅行需求,生成详细的旅行计划"
)
async def plan_trip(request: TripRequest):
    """
    生成旅行计划

    Args:
        request: 旅行请求参数

    Returns:
        旅行计划响应
    """
    try:
        print(f"\n{'='*60}")
        print(f"📥 收到旅行规划请求:")
        print(f"   城市: {request.city}")
        print(f"   日期: {request.start_date} - {request.end_date}")
        print(f"   天数: {request.travel_days}")
        print(f"{'='*60}\n")

        # 获取Agent实例
        print("🔄 获取多智能体系统实例...")
        agent = get_trip_planner_agent()

        # 生成旅行计划
        print("🚀 开始生成旅行计划...")
        trip_plan = agent.plan_trip(request)

        print("✅ 旅行计划生成成功,准备返回响应")
        
        # 调试：打印trip_plan的基本信息
        print(f"🔍 调试信息:")
        print(f"   trip_plan类型: {type(trip_plan)}")
        print(f"   city: {trip_plan.city}")
        print(f"   days数量: {len(trip_plan.days)}")
        print(f"   weather_info数量: {len(trip_plan.weather_info)}")
        print(f"   overall_suggestions长度: {len(trip_plan.overall_suggestions)}")
        print(f"   budget: {trip_plan.budget}")
        
        # 调试：检查days的完整性
        for i, day in enumerate(trip_plan.days):
            print(f"   Day {i}: attractions={len(day.attractions)}, meals={len(day.meals)}, hotel={day.hotel is not None}")
        
        # 调试：转换为JSON检查
        try:
            import json
            response_data = TripPlanResponse(
                success=True,
                message="旅行计划生成成功",
                data=trip_plan
            )
            json_str = json.dumps(response_data.model_dump(), ensure_ascii=False, indent=2)
            print(f"   JSON长度: {len(json_str)} 字符")
            print(f"   JSON前500字符: {json_str[:500]}...")
        except Exception as e:
            print(f"   ⚠️ JSON序列化失败: {str(e)}")
        
        print()

        return TripPlanResponse(
            success=True,
            message="旅行计划生成成功",
            data=trip_plan
        )

    except Exception as e:
        print(f"❌ 生成旅行计划失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"生成旅行计划失败: {str(e)}"
        )


@router.get(
    "/health",
    summary="健康检查",
    description="检查旅行规划服务是否正常"
)
async def health_check():
    """健康检查"""
    try:
        # 检查Agent是否可用
        agent = get_trip_planner_agent()
        
        return {
            "status": "healthy",
            "service": "trip-planner",
            "agent_name": agent.agent.name,
            "tools_count": len(agent.agent.list_tools())
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"服务不可用: {str(e)}"
        )

