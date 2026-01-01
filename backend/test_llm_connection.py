"""测试LLM API连接"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from hello_agents import HelloAgentsLLM

def test_llm_connection():
    """测试LLM API连接"""
    print("="*60)
    print("🔍 测试LLM API连接")
    print("="*60)
    
    # 检查环境变量
    print("\n📋 环境变量检查:")
    llm_api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    llm_base_url = os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    llm_model = os.getenv("LLM_MODEL_ID") or os.getenv("OPENAI_MODEL", "gpt-4")
    
    print(f"  LLM_API_KEY: {'✅ 已设置' if llm_api_key else '❌ 未设置'}")
    print(f"  LLM_BASE_URL: {llm_base_url}")
    print(f"  LLM_MODEL_ID: {llm_model}")
    
    if not llm_api_key:
        print("\n❌ 错误: LLM_API_KEY未设置")
        return False
    
    try:
        # 创建LLM实例
        print("\n🔄 创建LLM实例...")
        llm = HelloAgentsLLM()
        print(f"  ✅ LLM实例创建成功")
        print(f"     提供商: {llm.provider}")
        print(f"     模型: {llm.model}")
        
        # 测试简单调用
        print("\n🧪 测试简单API调用...")
        test_messages = [
            {"role": "user", "content": "请回复'连接成功'"}
        ]
        
        print("  发送请求...")
        response = llm.invoke(test_messages, timeout=30)
        print(f"  ✅ API调用成功!")
        print(f"     响应: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ API调用失败:")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误信息: {str(e)}")
        
        # 检查是否是超时错误
        if "timeout" in str(e).lower() or "timed out" in str(e).lower():
            print("\n⚠️  这是超时错误，可能的原因:")
            print("   1. API服务器响应慢")
            print("   2. 网络连接问题")
            print("   3. API服务不可用")
            print("   4. API Key无效或过期")
        
        # 检查是否是认证错误
        elif "401" in str(e) or "unauthorized" in str(e).lower() or "authentication" in str(e).lower():
            print("\n⚠️  这是认证错误，可能的原因:")
            print("   1. API Key无效或过期")
            print("   2. API Key格式错误")
        
        # 检查是否是连接错误
        elif "connection" in str(e).lower() or "connect" in str(e).lower():
            print("\n⚠️  这是连接错误，可能的原因:")
            print("   1. 网络连接问题")
            print("   2. API服务器地址错误")
            print("   3. 防火墙阻止连接")
        
        import traceback
        print("\n详细错误信息:")
        traceback.print_exc()
        
        return False

if __name__ == "__main__":
    success = test_llm_connection()
    print("\n" + "="*60)
    if success:
        print("✅ LLM API连接测试通过")
    else:
        print("❌ LLM API连接测试失败")
    print("="*60)
    sys.exit(0 if success else 1)

