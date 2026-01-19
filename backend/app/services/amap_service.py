"""Amap MCP Service Wrapper - LangChain Version"""

from typing import List, Dict, Any, Optional
import json
import shutil
from ..config import get_settings
from ..models.schemas import Location, POIInfo, WeatherInfo
from .mcp_client import get_mcp_client

# Global MCP client instance
_mcp_client = None


def get_mcp_client_instance():
    """
    Get Amap MCP client instance (singleton pattern)
    
    Returns:
        MCPClient instance
    """
    global _mcp_client
    
    if _mcp_client is None:
        settings = get_settings()
        
        if not settings.amap_api_key:
            raise ValueError("Amap API Key not configured. Please set AMAP_MAPS_API_KEY in .env file")
        
        # Check if uvx command exists
        uvx_path = shutil.which("uvx")
        if not uvx_path:
            raise RuntimeError(
                "uvx command not found. Please install uv: "
                "curl -LsSf https://astral.sh/uv/install.sh | sh"
            )
        
        # Create MCP client
        env_dict = {"AMAP_MAPS_API_KEY": settings.amap_api_key}
        _mcp_client = get_mcp_client([uvx_path, "amap-mcp-server"], env_dict)
        
        print(f"✅ Amap MCP client initialized successfully")
    
    return _mcp_client


class AmapService:
    """Amap Service Wrapper Class - LangChain Version"""
    
    def __init__(self):
        """Initialize service"""
        self.mcp_client = get_mcp_client_instance()
    
    def search_poi(self, keywords: str, city: str, citylimit: bool = True) -> List[POIInfo]:
        """
        Search POI
        
        Args:
            keywords: Search keywords
            city: City name
            citylimit: Whether to limit search within city boundaries
            
        Returns:
            List of POI information
        """
        try:
            # Call MCP tool
            result = self.mcp_client.call_tool(
                tool_name="maps_text_search",
                arguments={
                    "keywords": keywords,
                    "city": city,
                    "citylimit": str(citylimit).lower()
                }
            )
            
            # Parse result
            result_str = ""
            if "content" in result:
                content = result["content"]
                if isinstance(content, list) and len(content) > 0:
                    result_str = content[0].get("text", json.dumps(content, ensure_ascii=False))
                elif isinstance(content, str):
                    result_str = content
                else:
                    result_str = json.dumps(content, ensure_ascii=False)
            elif "text" in result:
                result_str = result["text"]
            else:
                result_str = json.dumps(result, ensure_ascii=False)
            
            print(f"POI search result: {result_str[:200]}...")
            
            # TODO: Parse actual POI data
            return []
            
        except Exception as e:
            print(f"❌ POI search failed: {str(e)}")
            return []
    
    def get_weather(self, city: str) -> List[WeatherInfo]:
        """
        Query weather
        
        Args:
            city: City name
            
        Returns:
            List of weather information
        """
        try:
            # Call MCP tool
            result = self.mcp_client.call_tool(
                tool_name="maps_weather",
                arguments={
                    "city": city
                }
            )
            
            # Parse result
            result_str = ""
            if "content" in result:
                content = result["content"]
                if isinstance(content, list) and len(content) > 0:
                    result_str = content[0].get("text", json.dumps(content, ensure_ascii=False))
                elif isinstance(content, str):
                    result_str = content
                else:
                    result_str = json.dumps(content, ensure_ascii=False)
            elif "text" in result:
                result_str = result["text"]
            else:
                result_str = json.dumps(result, ensure_ascii=False)
            
            print(f"Weather query result: {result_str[:200]}...")
            
            # TODO: Parse actual weather data
            return []
            
        except Exception as e:
            print(f"❌ Weather query failed: {str(e)}")
            return []
    
    def plan_route(
        self,
        origin_address: str,
        destination_address: str,
        origin_city: Optional[str] = None,
        destination_city: Optional[str] = None,
        route_type: str = "walking"
    ) -> Dict[str, Any]:
        """
        Plan route
        
        Args:
            origin_address: Origin address
            destination_address: Destination address
            origin_city: Origin city
            destination_city: Destination city
            route_type: Route type (walking/driving/transit)
            
        Returns:
            Route information
        """
        try:
            # Select tool based on route type
            tool_map = {
                "walking": "maps_direction_walking_by_address",
                "driving": "maps_direction_driving_by_address",
                "transit": "maps_direction_transit_integrated_by_address"
            }
            
            tool_name = tool_map.get(route_type, "maps_direction_walking_by_address")
            
            # Build arguments
            arguments = {
                "origin_address": origin_address,
                "destination_address": destination_address
            }
            
            # Public transit needs city parameters
            if route_type == "transit":
                if origin_city:
                    arguments["origin_city"] = origin_city
                if destination_city:
                    arguments["destination_city"] = destination_city
            else:
                # Other route types can also provide city parameters for better accuracy
                if origin_city:
                    arguments["origin_city"] = origin_city
                if destination_city:
                    arguments["destination_city"] = destination_city
            
            # Call MCP tool
            result = self.mcp_client.call_tool(
                tool_name=tool_name,
                arguments=arguments
            )
            
            # Parse result
            result_str = ""
            if "content" in result:
                content = result["content"]
                if isinstance(content, list) and len(content) > 0:
                    result_str = content[0].get("text", json.dumps(content, ensure_ascii=False))
                elif isinstance(content, str):
                    result_str = content
                else:
                    result_str = json.dumps(content, ensure_ascii=False)
            elif "text" in result:
                result_str = result["text"]
            else:
                result_str = json.dumps(result, ensure_ascii=False)
            
            print(f"Route planning result: {result_str[:200]}...")
            
            # TODO: Parse actual route data
            return {}
            
        except Exception as e:
            print(f"❌ Route planning failed: {str(e)}")
            return {}
    
    def geocode(self, address: str, city: Optional[str] = None) -> Optional[Location]:
        """
        Geocode (address to coordinates)

        Args:
            address: Address
            city: City

        Returns:
            Longitude and latitude coordinates
        """
        try:
            arguments = {"address": address}
            if city:
                arguments["city"] = city

            result = self.mcp_client.call_tool(
                tool_name="maps_geo",
                arguments=arguments
            )

            # Parse result
            result_str = ""
            if "content" in result:
                content = result["content"]
                if isinstance(content, list) and len(content) > 0:
                    result_str = content[0].get("text", json.dumps(content, ensure_ascii=False))
                elif isinstance(content, str):
                    result_str = content
                else:
                    result_str = json.dumps(content, ensure_ascii=False)
            elif "text" in result:
                result_str = result["text"]
            else:
                result_str = json.dumps(result, ensure_ascii=False)

            print(f"Geocode result: {result_str[:200]}...")

            # TODO: Parse actual coordinate data
            return None

        except Exception as e:
            print(f"❌ Geocode failed: {str(e)}")
            return None

    def get_poi_detail(self, poi_id: str) -> Dict[str, Any]:
        """
        Get POI details

        Args:
            poi_id: POI ID

        Returns:
            POI detail information
        """
        try:
            result = self.mcp_client.call_tool(
                tool_name="maps_search_detail",
                arguments={
                    "id": poi_id
                }
            )

            # Parse result
            result_str = ""
            if "content" in result:
                content = result["content"]
                if isinstance(content, list) and len(content) > 0:
                    result_str = content[0].get("text", json.dumps(content, ensure_ascii=False))
                elif isinstance(content, str):
                    result_str = content
                else:
                    result_str = json.dumps(content, ensure_ascii=False)
            elif "text" in result:
                result_str = result["text"]
            else:
                result_str = json.dumps(result, ensure_ascii=False)

            print(f"POI detail result: {result_str[:200]}...")

            # Parse result and extract images
            import re

            # Try to extract JSON from result
            json_match = re.search(r'\{.*\}', result_str, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data

            return {"raw": result_str}

        except Exception as e:
            print(f"❌ Failed to get POI details: {str(e)}")
            return {}


# 创建全局服务实例
_amap_service = None


def get_amap_service() -> AmapService:
    """Get Amap service instance (singleton pattern)"""
    global _amap_service
    
    if _amap_service is None:
        _amap_service = AmapService()
    
    return _amap_service

