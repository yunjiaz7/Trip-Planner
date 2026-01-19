"""
诊断脚本 - 检查MCP工具和Agent调用问题

检查点：
1. MCP工具是否能正确调用
2. 英文城市名是否能被高德地图API识别
3. Agent是否能正确调用工具
4. 工具返回结果的格式
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.mcp_tools import AmapTextSearchTool, AmapWeatherTool
from app.services.mcp_client import get_mcp_client
import shutil
import json

def test_mcp_tool_direct_call():
    """测试1: 直接调用MCP工具（英文城市名）"""
    print("=" * 60)
    print("Test 1: Direct MCP Tool Call (English City Name)")
    print("=" * 60)
    
    try:
        tool = AmapTextSearchTool()
        
        # 测试英文城市名
        print("\n1. Testing with English city name 'Beijing':")
        result = tool._run(keywords="attractions", city="Beijing", citylimit="true")
        print(f"   Result type: {type(result)}")
        print(f"   Result length: {len(result)}")
        print(f"   Result preview: {result[:300]}...")
        
        # 检查结果
        if "error" in result.lower():
            print("   ❌ Error found in result")
        elif "no results" in result.lower() or "not found" in result.lower():
            print("   ⚠️  No results found")
        else:
            print("   ✅ Result looks good")
        
        # 测试中文城市名
        print("\n2. Testing with Chinese city name '北京':")
        result_cn = tool._run(keywords="景点", city="北京", citylimit="true")
        print(f"   Result type: {type(result_cn)}")
        print(f"   Result length: {len(result_cn)}")
        print(f"   Result preview: {result_cn[:300]}...")
        
        # 比较结果
        if len(result_cn) > len(result) * 2:
            print("   ⚠️  Chinese city name returns more results - may need city name translation")
        elif len(result) > len(result_cn) * 2:
            print("   ⚠️  English city name returns more results")
        else:
            print("   ✅ Results are similar")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_mcp_tool_weather():
    """测试2: 天气查询工具（英文城市名）"""
    print("\n" + "=" * 60)
    print("Test 2: Weather Tool Call (English City Name)")
    print("=" * 60)
    
    try:
        tool = AmapWeatherTool()
        
        # 测试英文城市名
        print("\n1. Testing with English city name 'Beijing':")
        result = tool._run(city="Beijing")
        print(f"   Result type: {type(result)}")
        print(f"   Result length: {len(result)}")
        print(f"   Result: {result}")
        
        # 测试中文城市名
        print("\n2. Testing with Chinese city name '北京':")
        result_cn = tool._run(city="北京")
        print(f"   Result type: {type(result_cn)}")
        print(f"   Result length: {len(result_cn)}")
        print(f"   Result: {result_cn}")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_agent_tool_calling():
    """测试3: Agent是否能正确调用工具"""
    print("\n" + "=" * 60)
    print("Test 3: Agent Tool Calling")
    print("=" * 60)
    
    try:
        from app.agents.trip_planner_agent import MultiAgentTripPlanner
        from app.models.schemas import TripRequest
        
        planner = MultiAgentTripPlanner()
        
        # 创建测试请求
        from datetime import datetime, timedelta
        start_date = datetime.now() + timedelta(days=7)
        end_date = start_date + timedelta(days=1)
        
        request = TripRequest(
            city="Beijing",  # 英文城市名
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            travel_days=1,
            preferences=["历史文化"],  # 中文偏好
            transportation="公共交通",
            accommodation="经济型酒店",
            budget=3000
        )
        
        print(f"\nTest request:")
        print(f"  City: {request.city}")
        print(f"  Preferences: {request.preferences}")
        
        # 测试attraction agent
        print("\n1. Testing Attraction Agent:")
        attraction_query = planner._build_attraction_query(request)
        print(f"   Query: {attraction_query}")
        
        print("\n   Calling agent...")
        attraction_response = planner.attraction_agent.run(attraction_query)
        print(f"   Response length: {len(attraction_response)}")
        print(f"   Response preview: {attraction_response[:500]}...")
        
        # 检查响应
        if "error" in attraction_response.lower():
            print("   ❌ Error in response")
        elif "no results" in attraction_response.lower():
            print("   ⚠️  No results")
        elif "beijing" in attraction_response.lower() or "北京" in attraction_response:
            print("   ✅ Response contains city name")
        else:
            print("   ⚠️  Response may not contain useful data")
        
        # 测试weather agent
        print("\n2. Testing Weather Agent:")
        weather_query = f"Get weather information for {request.city}"
        print(f"   Query: {weather_query}")
        
        print("\n   Calling agent...")
        weather_response = planner.weather_agent.run(weather_query)
        print(f"   Response length: {len(weather_response)}")
        print(f"   Response: {weather_response[:300]}...")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_city_name_translation():
    """测试4: 检查是否需要城市名翻译"""
    print("\n" + "=" * 60)
    print("Test 4: City Name Translation Check")
    print("=" * 60)
    
    city_map = {
        "Beijing": "北京",
        "Shanghai": "上海",
        "Guangzhou": "广州",
        "Shenzhen": "深圳",
        "Hangzhou": "杭州",
        "Chengdu": "成都"
    }
    
    print("\nCity name mapping:")
    for en, cn in city_map.items():
        print(f"  {en} -> {cn}")
    
    print("\n⚠️  If MCP tools require Chinese city names, we need to add translation logic")


def check_mcp_client_status():
    """测试5: 检查MCP客户端状态"""
    print("\n" + "=" * 60)
    print("Test 5: MCP Client Status Check")
    print("=" * 60)
    
    try:
        # 检查uvx
        uvx_path = shutil.which("uvx")
        if not uvx_path:
            print("❌ uvx command not found")
            return False
        print(f"✅ uvx found: {uvx_path}")
        
        # 检查MCP客户端是否能初始化
        from app.config import get_settings
        settings = get_settings()
        
        if not settings.amap_api_key:
            print("❌ AMAP_API_KEY not configured")
            return False
        print(f"✅ AMAP_API_KEY configured: {settings.amap_api_key[:10]}...")
        
        # 尝试获取MCP客户端
        env = {"AMAP_MAPS_API_KEY": settings.amap_api_key}
        mcp_client = get_mcp_client([uvx_path, "amap-mcp-server"], env)
        
        if mcp_client.initialized:
            print("✅ MCP client initialized successfully")
        else:
            print("⚠️  MCP client not initialized")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """主诊断函数"""
    print("\n" + "=" * 60)
    print("DIAGNOSIS: MCP Tool and Agent Calling Issues")
    print("=" * 60)
    print("\nThis script will check:")
    print("1. Direct MCP tool calls with English/Chinese city names")
    print("2. Weather tool calls")
    print("3. Agent tool calling behavior")
    print("4. City name translation requirements")
    print("5. MCP client status")
    
    results = []
    
    # Test 1: Direct MCP tool call
    results.append(("Direct MCP Tool Call", test_mcp_tool_direct_call()))
    
    # Test 2: Weather tool
    results.append(("Weather Tool Call", test_mcp_tool_weather()))
    
    # Test 3: Agent tool calling
    results.append(("Agent Tool Calling", test_agent_tool_calling()))
    
    # Test 4: City name translation
    test_city_name_translation()
    results.append(("City Name Translation", True))  # Info only
    
    # Test 5: MCP client status
    results.append(("MCP Client Status", check_mcp_client_status()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Diagnosis Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name}: {status}")
    
    print("\n" + "=" * 60)
    print("Key Findings:")
    print("=" * 60)
    print("1. Check if MCP tools require Chinese city names")
    print("2. Check if Agent is actually calling tools")
    print("3. Check tool response format")
    print("4. Check if errors are being caught and handled")
    print("=" * 60)


if __name__ == "__main__":
    main()
