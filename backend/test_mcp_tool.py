"""
MCP工具测试脚本

目的：
1. 验证MCP服务器是否能正常调用
2. 测试LangChain Tool封装是否正确
3. 验证工具调用流程

使用方法：
    python test_mcp_tool.py
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.mcp_tools import AmapTextSearchTool, AmapWeatherTool
from app.config import get_settings


def test_mcp_server_connection():
    """测试MCP服务器连接"""
    print("=" * 60)
    print("测试1: MCP服务器连接")
    print("=" * 60)
    
    settings = get_settings()
    
    if not settings.amap_api_key:
        print("❌ AMAP_API_KEY未配置，请设置环境变量")
        return False
    
    print(f"✅ AMAP_API_KEY已配置: {settings.amap_api_key[:10]}...")
    
    # 测试uvx命令是否可用
    import subprocess
    try:
        result = subprocess.run(
            ["uvx", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ uvx命令可用: {result.stdout.strip()}")
        else:
            print(f"⚠️ uvx命令返回非零状态码: {result.stderr}")
    except FileNotFoundError:
        print("❌ uvx命令未找到，请安装uv: https://github.com/astral-sh/uv")
        return False
    except Exception as e:
        print(f"❌ 测试uvx命令失败: {str(e)}")
        return False
    
    return True


def test_amap_text_search_tool():
    """测试高德地图POI搜索工具"""
    print("\n" + "=" * 60)
    print("测试2: AmapTextSearchTool")
    print("=" * 60)
    
    tool = AmapTextSearchTool()
    
    print(f"工具名称: {tool.name}")
    print(f"工具描述: {tool.description}")
    print(f"参数schema: {tool.args_schema}")
    
    # 测试工具调用
    print("\n尝试调用工具...")
    print("参数: keywords='景点', city='北京'")
    
    try:
        result = tool._run(
            keywords="景点",
            city="北京",
            citylimit="true"
        )
        
        print(f"\n✅ 工具调用成功")
        print(f"返回结果长度: {len(result)} 字符")
        print(f"返回结果前200字符:\n{result[:200]}...")
        
        # 尝试解析JSON
        import json
        try:
            data = json.loads(result)
            print(f"\n✅ 返回结果是有效的JSON")
            print(f"JSON keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        except json.JSONDecodeError:
            print(f"\n⚠️ 返回结果不是JSON格式，可能是文本格式")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 工具调用失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_amap_weather_tool():
    """测试高德地图天气查询工具"""
    print("\n" + "=" * 60)
    print("测试3: AmapWeatherTool")
    print("=" * 60)
    
    tool = AmapWeatherTool()
    
    print(f"工具名称: {tool.name}")
    print(f"工具描述: {tool.description}")
    
    # 测试工具调用
    print("\n尝试调用工具...")
    print("参数: city='北京'")
    
    try:
        result = tool._run(city="北京")
        
        print(f"\n✅ 工具调用成功")
        print(f"返回结果长度: {len(result)} 字符")
        print(f"返回结果前200字符:\n{result[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 工具调用失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_langchain_tool_interface():
    """测试LangChain工具接口兼容性"""
    print("\n" + "=" * 60)
    print("测试4: LangChain工具接口兼容性")
    print("=" * 60)
    
    from langchain.tools import BaseTool
    
    tools = [
        AmapTextSearchTool(),
        AmapWeatherTool()
    ]
    
    print(f"✅ 创建了 {len(tools)} 个工具")
    
    for tool in tools:
        # 检查是否是BaseTool实例
        if isinstance(tool, BaseTool):
            print(f"✅ {tool.name} 是 BaseTool 实例")
        else:
            print(f"❌ {tool.name} 不是 BaseTool 实例")
            return False
        
        # 检查是否有必需的属性
        required_attrs = ['name', 'description', 'args_schema', '_run']
        for attr in required_attrs:
            if hasattr(tool, attr):
                print(f"  ✅ 有属性: {attr}")
            else:
                print(f"  ❌ 缺少属性: {attr}")
                return False
    
    print("\n✅ 所有工具都符合LangChain BaseTool接口")
    return True


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("MCP工具封装测试")
    print("=" * 60)
    
    results = []
    
    # 测试1: MCP服务器连接
    results.append(("MCP服务器连接", test_mcp_server_connection()))
    
    # 测试2: POI搜索工具
    results.append(("AmapTextSearchTool", test_amap_text_search_tool()))
    
    # 测试3: 天气查询工具
    results.append(("AmapWeatherTool", test_amap_weather_tool()))
    
    # 测试4: LangChain接口兼容性
    results.append(("LangChain接口兼容性", test_langchain_tool_interface()))
    
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
        print("\n🎉 所有测试通过！MCP工具封装成功")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息")
        return 1


if __name__ == "__main__":
    exit(main())
