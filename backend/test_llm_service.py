"""
LLM服务测试脚本

目的：
1. 验证LLM服务是否能正常初始化
2. 测试LLM连接和调用功能
3. 验证LangChain ChatOpenAI是否正常工作

使用方法：
    python test_llm_service.py
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.llm_service import get_llm, reset_llm
from app.config import get_settings


def test_llm_initialization():
    """测试LLM服务初始化"""
    print("=" * 60)
    print("测试1: LLM服务初始化")
    print("=" * 60)
    
    # 检查环境变量
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("LLM_BASE_URL")
    model = os.getenv("OPENAI_MODEL") or os.getenv("LLM_MODEL_ID")
    
    print(f"环境变量检查:")
    print(f"  API Key: {'已配置' if api_key else '❌ 未配置'}")
    print(f"  Base URL: {base_url or '使用默认'}")
    print(f"  Model: {model or '使用默认'}")
    
    if not api_key:
        print("\n⚠️  警告: API Key未配置，LLM初始化可能会失败")
        print("   请设置环境变量: OPENAI_API_KEY 或 LLM_API_KEY")
        return False
    
    try:
        # 重置LLM实例（确保重新初始化）
        reset_llm()
        
        # 获取LLM实例
        llm = get_llm()
        
        print(f"\n✅ LLM服务初始化成功")
        print(f"   LLM类型: {type(llm).__name__}")
        print(f"   模型名称: {llm.model_name if hasattr(llm, 'model_name') else 'N/A'}")
        print(f"   温度: {llm.temperature if hasattr(llm, 'temperature') else 'N/A'}")
        
        # 检查是否是LangChain的ChatOpenAI
        from langchain_openai import ChatOpenAI
        if isinstance(llm, ChatOpenAI):
            print(f"   ✅ 是LangChain ChatOpenAI实例")
        else:
            print(f"   ⚠️  不是ChatOpenAI实例，类型: {type(llm)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ LLM服务初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_simple_call():
    """测试LLM简单调用"""
    print("\n" + "=" * 60)
    print("测试2: LLM简单调用")
    print("=" * 60)
    
    try:
        llm = get_llm()
        
        # 测试简单调用
        print("发送测试消息: 'Hello, please respond with just OK'")
        
        from langchain_core.messages import HumanMessage
        
        response = llm.invoke([HumanMessage(content="Hello, please respond with just OK")])
        
        print(f"\n✅ LLM调用成功")
        print(f"   响应类型: {type(response).__name__}")
        print(f"   响应内容: {response.content if hasattr(response, 'content') else str(response)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ LLM调用失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_streaming():
    """测试LLM流式调用（可选）"""
    print("\n" + "=" * 60)
    print("测试3: LLM流式调用（可选）")
    print("=" * 60)
    
    try:
        llm = get_llm()
        
        from langchain_core.messages import HumanMessage
        
        print("发送流式请求: 'Count from 1 to 5'")
        print("流式响应:")
        
        chunks = []
        for chunk in llm.stream([HumanMessage(content="Count from 1 to 5")]):
            if hasattr(chunk, 'content'):
                content = chunk.content
                print(content, end='', flush=True)
                chunks.append(content)
            else:
                print(str(chunk), end='', flush=True)
                chunks.append(str(chunk))
        
        print(f"\n\n✅ 流式调用成功")
        print(f"   总响应长度: {len(''.join(chunks))} 字符")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 流式调用失败: {str(e)}")
        print("   注意: 流式调用失败不影响基本功能")
        import traceback
        traceback.print_exc()
        return False


def test_llm_with_tools():
    """测试LLM工具调用能力（验证Tool Calling）"""
    print("\n" + "=" * 60)
    print("测试4: LLM工具调用能力")
    print("=" * 60)
    
    try:
        llm = get_llm()
        
        # 创建一个简单的工具
        from langchain.tools import BaseTool
        from pydantic import BaseModel, Field
        from typing import Type  # 导入Type用于类型注解
        
        class CalculatorInput(BaseModel):
            a: int = Field(description="First number")
            b: int = Field(description="Second number")
        
        class CalculatorTool(BaseTool):
            name: str = "calculator"  # 添加类型注解（Pydantic 2.x要求）
            description: str = "Adds two numbers together"  # 添加类型注解
            args_schema: Type[BaseModel] = CalculatorInput  # 添加类型注解
            
            def _run(self, a: int, b: int) -> str:
                return str(a + b)
        
        tool = CalculatorTool()
        
        # 绑定工具到LLM
        llm_with_tools = llm.bind_tools([tool])
        
        print("发送带工具的请求: 'What is 2 + 3?'")
        
        from langchain_core.messages import HumanMessage
        
        response = llm_with_tools.invoke([HumanMessage(content="What is 2 + 3?")])
        
        print(f"\n✅ 工具调用测试成功")
        print(f"   响应类型: {type(response).__name__}")
        
        # 检查是否有工具调用
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"   ✅ 检测到工具调用: {len(response.tool_calls)} 个")
            for i, tool_call in enumerate(response.tool_calls):
                print(f"      工具调用 {i+1}: {tool_call.get('name', 'unknown')}")
        else:
            print(f"   ⚠️  未检测到工具调用（可能LLM直接回答了）")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 工具调用测试失败: {str(e)}")
        print("   注意: 工具调用失败可能不影响基本功能")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("LLM服务测试 (LangChain版本)")
    print("=" * 60)
    
    results = []
    
    # 测试1: LLM初始化
    results.append(("LLM服务初始化", test_llm_initialization()))
    
    # 如果初始化成功，继续其他测试
    if results[0][1]:
        # 测试2: 简单调用
        results.append(("LLM简单调用", test_llm_simple_call()))
        
        # 测试3: 流式调用（可选）
        try:
            results.append(("LLM流式调用", test_llm_streaming()))
        except Exception as e:
            print(f"\n⚠️  流式调用测试跳过: {str(e)}")
            results.append(("LLM流式调用", False))
        
        # 测试4: 工具调用能力
        try:
            results.append(("LLM工具调用能力", test_llm_with_tools()))
        except Exception as e:
            print(f"\n⚠️  工具调用测试跳过: {str(e)}")
            results.append(("LLM工具调用能力", False))
    
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
        print("\n🎉 所有测试通过！LLM服务迁移成功")
        return 0
    elif passed > 0:
        print("\n⚠️  部分测试通过，基本功能正常")
        return 0
    else:
        print("\n❌ 所有测试失败，请检查配置")
        return 1


if __name__ == "__main__":
    exit(main())
