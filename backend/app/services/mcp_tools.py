"""
MCP工具封装 - LangChain版本

修改逻辑和原因：
================

1. 为什么需要这个文件？
   - HelloAgents的MCPTool不能直接在LangChain中使用
   - 需要将MCP工具封装为LangChain的BaseTool格式
   - 保持工具功能不变，但接口适配LangChain框架

2. 实现方式选择：
   - 方案1：使用MCP Python SDK（如果可用）
   - 方案2：通过subprocess调用uvx amap-mcp-server
   - 方案3：直接调用MCP协议（需要研究协议细节）
   
   当前采用方案2（subprocess），因为：
   - 最简单直接
   - 不需要额外的SDK依赖
   - HelloAgents的MCPTool也是通过这种方式工作的

3. 工具设计原则：
   - 每个MCP工具封装为独立的BaseTool类
   - 保持与HelloAgents版本相同的功能
   - 接口适配LangChain的Tool Calling标准
"""

import json
import subprocess
import os
from typing import Optional, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from ..config import get_settings
from .mcp_client import get_mcp_client
from ..utils.city_translator import translate_city_name


class AmapTextSearchInput(BaseModel):
    """高德地图POI搜索工具输入参数"""
    keywords: str = Field(description="Search keywords, e.g., 'attractions', 'restaurants', 'hotels'")
    city: str = Field(description="City name, e.g., 'Beijing', 'Shanghai'")
    citylimit: str = Field(default="true", description="Whether to limit search within city boundaries")


class AmapTextSearchTool(BaseTool):
    """
    高德地图POI搜索工具 - LangChain版本
    
    功能：搜索高德地图的POI（景点、餐厅、酒店等）
    
    修改说明：
    - 从HelloAgents框架迁移到LangChain的BaseTool
    - 保持相同的功能（调用amap-mcp-server的maps_text_search工具）
    - 适配LangChain的Tool Calling接口
    - 格式化返回结果，减少Agent重试
    """
    name: str = "amap_maps_text_search"
    description: str = (
        "Search for POIs (points of interest) in Amap. "
        "Use this tool to find attractions, restaurants, hotels, and other places. "
        "Input: keywords (what to search for) and city (where to search). "
        "Returns formatted list of POIs with names and addresses."
    )
    args_schema: Type[BaseModel] = AmapTextSearchInput
    
    def _run(
        self,
        keywords: str,
        city: str,
        citylimit: str = "true"
    ) -> str:
        """
        调用MCP服务器搜索POI
        
        实现逻辑：
        1. 使用MCP客户端（实现完整的MCP协议流程）
        2. 发送工具调用请求
        3. 返回搜索结果
        """
        try:
            settings = get_settings()
            
            # 检查uvx命令是否存在
            import shutil
            uvx_path = shutil.which("uvx")
            if not uvx_path:
                return json.dumps({
                    "error": "uvx command not found",
                    "message": "Please install uv: https://github.com/astral-sh/uv",
                    "install_command": "curl -LsSf https://astral.sh/uv/install.sh | sh"
                }, ensure_ascii=False)
            
            # 获取MCP客户端（单例模式，会自动初始化）
            env = {"AMAP_MAPS_API_KEY": settings.amap_api_key}
            mcp_client = get_mcp_client([uvx_path, "amap-mcp-server"], env)
            
            # Translate city name to Chinese for Amap API compatibility
            chinese_city = translate_city_name(city)
            print(f"   🔄 Translated city name: {city} -> {chinese_city}")
            
            # 调用工具
            # mcp_client.call_tool()返回的是字典，不是subprocess结果
            result = mcp_client.call_tool(
                tool_name="maps_text_search",
                arguments={
                    "keywords": keywords,
                    "city": chinese_city,  # Use Chinese city name
                    "citylimit": citylimit
                }
            )
            
            # 处理结果（result是字典，包含MCP协议响应）
            # MCP工具可能返回不同的格式，需要统一处理
            if "content" in result:
                content = result["content"]
                if isinstance(content, list):
                    # 如果是列表，检查是否包含文本内容
                    if len(content) > 0:
                        if isinstance(content[0], dict):
                            # 如果是字典列表，提取文本或格式化
                            text_content = content[0].get("text", "")
                            if text_content:
                                return text_content
                            # 如果没有text字段，格式化整个列表
                            return self._format_poi_results(content)
                        else:
                            return json.dumps(content, ensure_ascii=False)
                    return "No results found"
                elif isinstance(content, str):
                    return content
                else:
                    return json.dumps(content, ensure_ascii=False)
            elif "text" in result:
                return result["text"]
            elif "error" in result:
                # MCP协议错误响应
                error_info = result["error"]
                if isinstance(error_info, dict):
                    return json.dumps({
                        "error": "MCP protocol error",
                        "message": error_info.get("message", "Unknown error"),
                        "code": error_info.get("code", -1)
                    }, ensure_ascii=False)
                else:
                    return json.dumps({"error": str(error_info)}, ensure_ascii=False)
            else:
                # 检查是否直接包含POI数据
                if "pois" in result:
                    return self._format_poi_results(result["pois"])
                # 其他格式，直接返回
                return json.dumps(result, ensure_ascii=False)

        except Exception as e:
            return f"Error calling AmapTextSearchTool: {str(e)}"
    
    def _format_poi_results(self, pois: list) -> str:
        """
        格式化POI搜索结果，返回友好的文本格式
        
        这样Agent更容易理解结果，减少重试
        """
        if not pois:
            return "No POIs found"
        
        formatted_results = []
        for poi in pois[:10]:  # 只返回前10个结果
            name = poi.get("name", "Unknown")
            address = poi.get("address", "Address not available")
            formatted_results.append(f"- {name}\n  Address: {address}")
        
        return "\n".join(formatted_results)
    
    async def _arun(
        self,
        keywords: str,
        city: str,
        citylimit: str = "true"
    ) -> str:
        """异步版本（暂时使用同步实现）"""
        return self._run(keywords, city, citylimit)


class AmapWeatherInput(BaseModel):
    """高德地图天气查询工具输入参数"""
    city: str = Field(description="City name to query weather for, e.g., 'Beijing', 'Shanghai'")


class AmapWeatherTool(BaseTool):
    """
    高德地图天气查询工具 - LangChain版本
    
    功能：查询指定城市的天气信息
    
    修改说明：
    - 从HelloAgents框架迁移到LangChain的BaseTool
    - 保持相同的功能（调用amap-mcp-server的maps_weather工具）
    """
    name: str = "amap_maps_weather"
    description: str = (
        "Get weather information for a city from Amap. "
        "Input: city name. Returns weather forecast including temperature, conditions, wind, etc."
    )
    args_schema: Type[BaseModel] = AmapWeatherInput
    
    def _run(self, city: str) -> str:
        """调用MCP服务器查询天气"""
        try:
            settings = get_settings()
            
            # 检查uvx命令是否存在
            import shutil
            uvx_path = shutil.which("uvx")
            if not uvx_path:
                return json.dumps({
                    "error": "uvx command not found",
                    "message": "Please install uv: https://github.com/astral-sh/uv",
                    "install_command": "curl -LsSf https://astral.sh/uv/install.sh | sh"
                }, ensure_ascii=False)
            
            # 获取MCP客户端（单例模式，会自动初始化）
            env_dict = {"AMAP_MAPS_API_KEY": settings.amap_api_key}
            mcp_client = get_mcp_client([uvx_path, "amap-mcp-server"], env_dict)
            
            # Translate city name to Chinese - Weather API REQUIRES Chinese city names
            chinese_city = translate_city_name(city)
            print(f"   🔄 Translated city name: {city} -> {chinese_city}")
            
            # 调用工具
            result = mcp_client.call_tool(
                tool_name="maps_weather",
                arguments={"city": chinese_city}  # Use Chinese city name (required for weather API)
            )
            
            # 处理结果
            if "content" in result:
                content = result["content"]
                if isinstance(content, list):
                    if len(content) > 0 and isinstance(content[0], dict):
                        return content[0].get("text", json.dumps(content, ensure_ascii=False))
                    return json.dumps(content, ensure_ascii=False)
                elif isinstance(content, str):
                    return content
                else:
                    return json.dumps(content, ensure_ascii=False)
            elif "text" in result:
                return result["text"]
            else:
                return json.dumps(result, ensure_ascii=False)

        except Exception as e:
            return f"Error calling AmapWeatherTool: {str(e)}"
    
    async def _arun(self, city: str) -> str:
        """异步版本"""
        return self._run(city)


def get_amap_tools() -> list[BaseTool]:
    """
    获取所有高德地图MCP工具的列表
    
    返回：
        List[BaseTool]: LangChain工具列表
        
    修改说明：
    - 替代原来的MCPTool（HelloAgents版本）
    - 返回LangChain兼容的工具列表
    - 可以传递给AgentExecutor使用
    """
    return [
        AmapTextSearchTool(),
        AmapWeatherTool(),
        # 其他工具可以在这里添加
    ]
