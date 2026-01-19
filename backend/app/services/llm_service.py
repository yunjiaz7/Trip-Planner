"""
LLM服务模块 - LangChain版本

修改逻辑和原因：
================

1. 为什么需要迁移？
   - HelloAgents的HelloAgentsLLM不能在LangChain中直接使用
   - LangChain需要标准的ChatOpenAI或兼容的LLM接口
   - 保持接口不变（get_llm()函数签名），但内部实现改为LangChain

2. 实现方式：
   - 使用langchain_openai.ChatOpenAI替代HelloAgentsLLM
   - 保持相同的配置方式（从环境变量读取）
   - 保持超时时间设置（300秒）
   - 支持多种LLM提供商（OpenAI、DeepSeek等）

3. 兼容性：
   - 保持get_llm()函数接口不变
   - 返回类型改为ChatOpenAI（但函数签名可以保持兼容）
   - 确保现有代码可以无缝迁移
"""

import os
from typing import Union
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from ..config import get_settings

# 全局LLM实例
_llm_instance: Union[BaseChatModel, None] = None


def get_llm() -> BaseChatModel:
    """
    获取LLM实例(单例模式) - LangChain版本
    
    修改说明：
    - 从HelloAgentsLLM改为LangChain的ChatOpenAI
    - 保持相同的配置方式（从环境变量读取）
    - 支持OpenAI、DeepSeek等兼容OpenAI API的提供商
    
    Returns:
        ChatOpenAI实例（LangChain标准接口）
    """
    global _llm_instance
    
    if _llm_instance is None:
        settings = get_settings()
        
        # 从环境变量读取配置（兼容HelloAgents的配置方式）
        # 支持的环境变量：
        # - OPENAI_API_KEY 或 LLM_API_KEY
        # - OPENAI_BASE_URL 或 LLM_BASE_URL
        # - OPENAI_MODEL 或 LLM_MODEL_ID
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY") or settings.openai_api_key
        base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("LLM_BASE_URL") or settings.openai_base_url
        model = os.getenv("OPENAI_MODEL") or os.getenv("LLM_MODEL_ID") or settings.openai_model
        
        if not api_key:
            raise ValueError(
                "LLM API Key not configured. Please set environment variable: "
                "OPENAI_API_KEY or LLM_API_KEY"
            )
        
        # 创建LangChain ChatOpenAI实例
        # 注意：ChatOpenAI支持任何兼容OpenAI API的提供商（如DeepSeek）
        llm_kwargs = {
            "model": model,
            "temperature": 0,  # 设置为0以获得更确定性的输出
            "timeout": 300,    # 5分钟超时，用于处理复杂的行程规划任务
            "api_key": api_key,
        }
        
        # 如果base_url不是默认的OpenAI URL，则设置base_url
        # 这允许使用DeepSeek等兼容OpenAI API的提供商
        if base_url and base_url != "https://api.openai.com/v1":
            llm_kwargs["base_url"] = base_url
        
        _llm_instance = ChatOpenAI(**llm_kwargs)
        
        print(f"✅ LLM service initialized successfully (LangChain version)")
        print(f"   Model: {model}")
        print(f"   Base URL: {base_url}")
        print(f"   Timeout: 300 seconds")
        print(f"   API Key: {'Configured' if api_key else 'Not configured'}")
    
    return _llm_instance


def reset_llm():
    """
    重置LLM实例(用于测试或重新配置)
    
    修改说明：
    - 保持接口不变，功能相同
    """
    global _llm_instance
    _llm_instance = None

