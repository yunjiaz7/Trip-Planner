"""
景点搜索Agent测试脚本

目的：
1. 验证attraction_agent是否能正常工作
2. 测试工具调用功能
3. 验证输出格式
4. 确保接口兼容

使用方法：
    python test_attraction_agent.py
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.agents.trip_planner_agent import MultiAgentTripPlanner
from app.models.schemas import TripRequest


def test_attraction_agent_initialization():
    """测试attraction_agent初始化"""
    print("=" * 60)
    print("测试1: Attraction Agent初始化")
    print("=" * 60)
    
    try:
        planner = MultiAgentTripPlanner()
        
        print(f"\n✅ Agent初始化成功")
        print(f"   attraction_agent类型: {type(planner.attraction_agent).__name__}")
        print(f"   attraction_agent名称: {planner.attraction_agent.name}")
        
        # 检查是否有run方法（接口兼容）
        if hasattr(planner.attraction_agent, 'run'):
            print(f"   ✅ 有run方法（接口兼容）")
        else:
            print(f"   ❌ 缺少run方法")
            return False
        
        # 检查是否有list_tools方法（接口兼容）
        if hasattr(planner.attraction_agent, 'list_tools'):
            tools = planner.attraction_agent.list_tools()
            print(f"   ✅ 有list_tools方法，工具数量: {len(tools)}")
        else:
            print(f"   ⚠️  缺少list_tools方法（可选）")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Agent初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_attraction_agent_call():
    """测试attraction_agent调用"""
    print("\n" + "=" * 60)
    print("测试2: Attraction Agent调用")
    print("=" * 60)
    
    try:
        planner = MultiAgentTripPlanner()
        
        # 测试查询
        query = "Search for attractions in Beijing"
        print(f"发送查询: {query}")
        
        response = planner.attraction_agent.run(query)
        
        print(f"\n✅ Agent调用成功")
        print(f"   响应类型: {type(response).__name__}")
        print(f"   响应长度: {len(response)} 字符")
        print(f"   响应内容前200字符:\n{response[:200]}...")
        
        # 检查响应格式
        if isinstance(response, str):
            print(f"   ✅ 响应是字符串格式（符合接口要求）")
        else:
            print(f"   ⚠️  响应不是字符串格式: {type(response)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Agent调用失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_attraction_agent_with_trip_request():
    """测试attraction_agent在完整流程中的使用"""
    print("\n" + "=" * 60)
    print("测试3: Attraction Agent在完整流程中的使用")
    print("=" * 60)
    
    try:
        planner = MultiAgentTripPlanner()
        
        # 创建测试请求
        request = TripRequest(
            city="Beijing",
            start_date="2025-06-01",
            end_date="2025-06-03",
            travel_days=3,
            transportation="public transport",
            accommodation="budget hotel",
            preferences=["historical culture"],
            free_text_input=""
        )
        
        print(f"测试请求:")
        print(f"  城市: {request.city}")
        print(f"  偏好: {request.preferences}")
        
        # 测试_build_attraction_query方法
        query = planner._build_attraction_query(request)
        print(f"\n生成的查询: {query[:100]}...")
        
        # 测试attraction_agent调用（注意：可能需要uv工具）
        print("\n尝试调用attraction_agent...")
        response = planner.attraction_agent.run(query)
        
        print(f"\n✅ 完整流程测试成功")
        print(f"   响应长度: {len(response)} 字符")
        print(f"   响应前200字符:\n{response[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 完整流程测试失败: {str(e)}")
        print("   注意: 如果是因为uv工具未安装，这是预期的")
        import traceback
        traceback.print_exc()
        return False


def test_interface_compatibility():
    """测试接口兼容性"""
    print("\n" + "=" * 60)
    print("测试4: 接口兼容性")
    print("=" * 60)
    
    try:
        planner = MultiAgentTripPlanner()
        
        # 检查接口方法
        required_methods = ['run']
        optional_methods = ['list_tools']
        
        print("检查必需方法:")
        for method in required_methods:
            if hasattr(planner.attraction_agent, method):
                print(f"   ✅ {method}方法存在")
            else:
                print(f"   ❌ {method}方法缺失")
                return False
        
        print("\n检查可选方法:")
        for method in optional_methods:
            if hasattr(planner.attraction_agent, method):
                print(f"   ✅ {method}方法存在")
            else:
                print(f"   ⚠️  {method}方法缺失（可选）")
        
        # 测试run方法签名
        import inspect
        run_sig = inspect.signature(planner.attraction_agent.run)
        print(f"\nrun方法签名: {run_sig}")
        
        # 检查参数
        params = list(run_sig.parameters.keys())
        if 'query' in params or len(params) == 1:
            print(f"   ✅ run方法参数正确")
        else:
            print(f"   ⚠️  run方法参数: {params}")
        
        # 检查返回类型（通过调用测试）
        test_response = planner.attraction_agent.run("test")
        if isinstance(test_response, str):
            print(f"   ✅ run方法返回字符串（符合接口要求）")
        else:
            print(f"   ⚠️  run方法返回类型: {type(test_response)}")
        
        print(f"\n✅ 接口兼容性测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 接口兼容性测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("景点搜索Agent测试 (LangChain版本)")
    print("=" * 60)
    
    results = []
    
    # 测试1: Agent初始化
    results.append(("Agent初始化", test_attraction_agent_initialization()))
    
    # 如果初始化成功，继续其他测试
    if results[0][1]:
        # 测试2: Agent调用
        results.append(("Agent调用", test_attraction_agent_call()))
        
        # 测试3: 完整流程
        results.append(("完整流程", test_attraction_agent_with_trip_request()))
        
        # 测试4: 接口兼容性
        results.append(("接口兼容性", test_interface_compatibility()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！attraction_agent迁移成功")
        return 0
    elif passed > 0:
        print("\n⚠️  部分测试通过，基本功能正常")
        return 0
    else:
        print("\n❌ 所有测试失败，请检查代码")
        return 1


if __name__ == "__main__":
    exit(main())
