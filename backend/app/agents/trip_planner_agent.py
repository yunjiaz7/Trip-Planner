"""
多智能体旅行规划系统 - LangChain版本

迁移说明：
- 所有Agent已迁移到LangChain框架
- 不再依赖HelloAgents框架
- 所有提示词已改为英文
- 保持接口兼容（plan_trip方法不变）
"""

import json
from typing import Dict, Any, List, Optional

# LangChain框架
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage

# 项目模块
from ..services.llm_service import get_llm
from ..services.mcp_tools import get_amap_tools
from ..models.schemas import TripRequest, TripPlan, DayPlan, Attraction, Meal, WeatherInfo, Location, Hotel
from ..config import get_settings
from ..utils.city_translator import translate_city_name

# ============ Agent提示词 (英文版本) ============

ATTRACTION_AGENT_PROMPT = """You are an attraction search expert. Your task is to search for suitable attractions based on the city and user preferences.

**Important:**
You MUST use tools to search for attractions! Do not make up attraction information!

**Tool Usage:**
Use the amap_maps_text_search tool to search for POIs (points of interest) like attractions, restaurants, hotels, etc.

**CRITICAL - City Name Translation:**
- If the user provides an English city name (e.g., "Beijing", "Shanghai"), you MUST translate it to Chinese (e.g., "北京", "上海") when calling the tool
- The tool requires Chinese city names for accurate results
- The query may specify the Chinese city name - use that when calling the tool

**Examples:**
User: "Search for historical and cultural attractions in Beijing (use Chinese city name '北京' when calling the tool)"
You should: Use the amap_maps_text_search tool with keywords="historical culture" and city="北京"

User: "Search for parks in Shanghai (use Chinese city name '上海' when calling the tool)"
You should: Use the amap_maps_text_search tool with keywords="park" and city="上海"

**Notes:**
1. You MUST use tools, do not answer directly
2. Always use the tool to get real data
3. Use Chinese city names when calling the tool (as specified in the query)
4. Return the search results from the tool
5. **IMPORTANT**: If the tool returns results that don't match the requested city, try once more with different keywords, then accept the best available results. Do not retry more than 2-3 times.
"""

# 保留中文版本用于兼容（逐步移除）
ATTRACTION_AGENT_PROMPT_CN = """你是景点搜索专家。你的任务是根据城市和用户偏好搜索合适的景点。

**重要提示:**
你必须使用工具来搜索景点!不要自己编造景点信息!

**工具调用格式:**
使用maps_text_search工具时,必须严格按照以下格式:
`[TOOL_CALL:amap_maps_text_search:keywords=景点关键词,city=城市名]`

**示例:**
用户: "搜索北京的历史文化景点"
你的回复: [TOOL_CALL:amap_maps_text_search:keywords=历史文化,city=北京]

用户: "搜索上海的公园"
你的回复: [TOOL_CALL:amap_maps_text_search:keywords=公园,city=上海]

**注意:**
1. 必须使用工具,不要直接回答
2. 格式必须完全正确,包括方括号和冒号
3. 参数用逗号分隔
"""

WEATHER_AGENT_PROMPT = """You are a weather query expert. Your task is to query weather information for a specified city.

**Important:**
You MUST use tools to query weather! Do not make up weather information!

**Tool Usage:**
Use the amap_maps_weather tool to get weather forecast for a city.

**CRITICAL - City Name Translation:**
- The weather tool REQUIRES Chinese city names (e.g., "北京", "上海")
- If the query specifies a Chinese city name, use that exact name when calling the tool
- Do NOT use English city names - the tool will fail with English names

**Examples:**
User: "Get weather information for 北京 (city name: 北京). Please use the amap_maps_weather tool with city='北京'."
You should: Use the amap_maps_weather tool with city="北京"

User: "Get weather information for 上海 (city name: 上海). Please use the amap_maps_weather tool with city='上海'."
You should: Use the amap_maps_weather tool with city="上海"

**Notes:**
1. You MUST use tools, do not answer directly
2. Always use the tool to get real weather data
3. Use the Chinese city name as specified in the query when calling the tool
4. Return the weather information from the tool
"""

HOTEL_AGENT_PROMPT = """You are a hotel recommendation expert. Your task is to recommend suitable hotels based on the city and attraction locations.

**Important:**
You MUST use tools to search for hotels! Do not make up hotel information!

**Tool Usage:**
Use the amap_maps_text_search tool to search for hotels. Use keywords like "hotel", "inn", or specific hotel types.

**CRITICAL - City Name Translation:**
- If the query specifies a Chinese city name, use that exact name when calling the tool
- The tool works better with Chinese city names for accurate results
- The query may specify the Chinese city name - use that when calling the tool

**Examples:**
User: "Search for hotels in 北京 (city name: 北京). Please use the amap_maps_text_search tool with keywords='hotel' and city='北京'."
You should: Use the amap_maps_text_search tool with keywords="hotel" and city="北京"

User: "Search for hotels in 上海 (city name: 上海). Please use the amap_maps_text_search tool with keywords='hotel' and city='上海'."
You should: Use the amap_maps_text_search tool with keywords="hotel" and city="上海"

**Notes:**
1. You MUST use tools, do not answer directly
2. Always use the tool to get real hotel data
3. Use the Chinese city name as specified in the query when calling the tool
4. Return the hotel search results from the tool
5. **IMPORTANT**: If the tool returns results that don't match the requested city, try once more with different keywords, then accept the best available results. Do not retry more than 2-3 times.
"""

PLANNER_AGENT_PROMPT = """You are a trip planning expert. Your task is to generate a detailed travel plan based on attraction information and weather information.

**CRITICAL - Language Requirement:**
- ALL output must be in ENGLISH ONLY
- Translate ALL Chinese text to English, including:
  - Attraction names (e.g., "故宫博物院" -> "Forbidden City" or "Palace Museum")
  - Hotel names (e.g., "北京宝格丽酒店" -> "Beijing Bulgari Hotel")
  - Addresses (e.g., "景山前街4号" -> "4 Jingshan Front Street")
  - Weather descriptions (e.g., "晴" -> "Sunny", "北风" -> "North wind", "多云" -> "Cloudy")
  - All descriptions, suggestions, and text content
- Do NOT include any Chinese characters in the output
- Use proper English translations for all place names and descriptions

Please strictly follow the following JSON format to return the travel plan:
```json
{{
  "city": "City Name",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "days": [
    {{
      "date": "YYYY-MM-DD",
      "day_index": 0,
      "description": "Day 1 itinerary overview",
      "transportation": "Transportation method",
      "accommodation": "Accommodation type",
      "hotel": {{
        "name": "Hotel Name",
        "address": "Hotel Address",
        "location": {{"longitude": 116.397128, "latitude": 39.916527}},
        "price_range": "300-500 CNY",
        "rating": "4.5",
        "distance": "2 km from attractions",
        "type": "Budget Hotel",
        "estimated_cost": 400
      }},
      "attractions": [
        {{
          "name": "Attraction Name",
          "address": "Detailed Address",
          "location": {{"longitude": 116.397128, "latitude": 39.916527}},
          "visit_duration": 120,
          "description": "Detailed attraction description",
          "category": "Attraction Category",
          "ticket_price": 60
        }}
      ],
      "meals": [
        {{"type": "breakfast", "name": "Breakfast Recommendation", "description": "Breakfast description", "estimated_cost": 30}},
        {{"type": "lunch", "name": "Lunch Recommendation", "description": "Lunch description", "estimated_cost": 50}},
        {{"type": "dinner", "name": "Dinner Recommendation", "description": "Dinner description", "estimated_cost": 80}}
      ]
    }}
  ],
  "weather_info": [
    {{
      "date": "YYYY-MM-DD",
      "day_weather": "Sunny",
      "night_weather": "Cloudy",
      "day_temp": 25,
      "night_temp": 15,
      "wind_direction": "South",
      "wind_power": "1-3 level"
    }}
  ],
  "overall_suggestions": "Overall suggestions",
  "budget": {{
    "total_attractions": 180,
    "total_hotels": 1200,
    "total_meals": 480,
    "total_transportation": 200,
    "total": 2060
  }}
}}
```

**Important Notes:**
1. **ALL text must be in English** - Translate all Chinese content from the input data
2. The weather_info array must contain weather information for each day (in English)
3. Temperature must be a pure number (do not include units like °C)
4. Arrange 2-3 attractions per day
5. Consider the distance between attractions and visiting time
6. Each day must include breakfast, lunch, and dinner
7. Provide practical travel suggestions (in English)
8. **Must include budget information**:
   - Attraction ticket prices (ticket_price)
   - Meal estimated costs (estimated_cost)
   - Hotel estimated costs (estimated_cost)
   - Budget summary (budget) including total costs for each category
9. **Translation Guidelines**:
   - Use well-known English names for famous attractions (e.g., "Forbidden City" for "故宫")
   - Translate hotel names accurately (keep brand names, translate location names)
   - Translate addresses to English format (street names, building numbers)
   - Weather terms: "晴"->"Sunny", "多云"->"Cloudy", "雨"->"Rainy", "雪"->"Snowy"
   - Wind directions: "北"->"North", "南"->"South", "东"->"East", "西"->"West"
"""


class MultiAgentTripPlanner:
    """多智能体旅行规划系统"""

    def __init__(self):
        """初始化多智能体系统"""
        print("🔄 Initializing multi-agent trip planning system...")

        try:
            settings = get_settings()
            self.llm = get_llm()

            # Create shared MCP tools (create once)
            print("  - Creating shared MCP tools...")
            self.amap_tools = get_amap_tools()
            print(f"  - LangChain tools count: {len(self.amap_tools)}")

            # Create attraction search Agent - LangChain version
            print("  - Creating attraction search Agent (LangChain version)...")
            self.attraction_agent = self._create_langchain_agent(
                system_prompt=ATTRACTION_AGENT_PROMPT,
                tools=self.amap_tools,
                agent_name="Attraction Search Expert"
            )

            # Create weather query Agent - LangChain version
            print("  - Creating weather query Agent (LangChain version)...")
            self.weather_agent = self._create_langchain_agent(
                system_prompt=WEATHER_AGENT_PROMPT,
                tools=self.amap_tools,
                agent_name="Weather Query Expert"
            )

            # Create hotel recommendation Agent - LangChain version
            print("  - Creating hotel recommendation Agent (LangChain version)...")
            self.hotel_agent = self._create_langchain_agent(
                system_prompt=HOTEL_AGENT_PROMPT,
                tools=self.amap_tools,
                agent_name="Hotel Recommendation Expert"
            )

            # Create trip planning Agent - LangChain version (no tools needed)
            # Note: For agents without tools, we use LLMChain instead of AgentExecutor
            # because create_openai_tools_agent doesn't support empty tools list
            print("  - Creating trip planning Agent (LangChain version, no tools)...")
            self.planner_agent = self._create_llm_chain_agent(
                system_prompt=PLANNER_AGENT_PROMPT,
                agent_name="Trip Planning Expert"
            )

            print(f"✅ Multi-agent system initialized successfully (all using LangChain version)")
            print(f"   Attraction search Agent: LangChain version ({len(self.amap_tools)} tools)")
            print(f"   Weather query Agent: LangChain version ({len(self.amap_tools)} tools)")
            print(f"   Hotel recommendation Agent: LangChain version ({len(self.amap_tools)} tools)")
            print(f"   Trip planning Agent: LangChain version (0 tools)")

        except Exception as e:
            print(f"❌ Multi-agent system initialization failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def _create_langchain_agent(
        self,
        system_prompt: str,
        tools: List,
        agent_name: str
    ) -> AgentExecutor:
        """
        创建LangChain Agent
        
        修改说明：
        - 使用LangChain的AgentExecutor替代HelloAgents框架
        - 保持接口兼容（通过包装器实现run方法）
        - 使用标准提示词模板，包含agent_scratchpad变量
        
        Args:
            system_prompt: 系统提示词
            tools: 工具列表
            agent_name: Agent名称
            
        Returns:
            AgentExecutor实例（带run方法包装）
        """
        # 创建提示词模板
        # 注意：create_openai_tools_agent需要包含agent_scratchpad变量
        # 使用MessagesPlaceholder来添加agent_scratchpad
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")  # 添加agent_scratchpad占位符
        ])
        
        # 创建Agent
        agent = create_openai_tools_agent(self.llm, tools, prompt)
        
        # 创建AgentExecutor
        # 设置合理的迭代限制，避免无限重试
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,  # 限制最多3次迭代，避免过多LLM调用
            max_execution_time=30  # 限制最多30秒执行时间
        )
        
        # 包装AgentExecutor，添加run方法以保持接口兼容
        class AgentWrapper:
            """Agent包装器，保持与原有接口兼容"""
            def __init__(self, executor: AgentExecutor, name: str):
                self.executor = executor
                self.name = name
            
            def run(self, query: str) -> str:
                """
                运行Agent，返回字符串结果
                
                保持与原有接口兼容
                """
                try:
                    result = self.executor.invoke({"input": query})
                    # 提取输出内容
                    if isinstance(result, dict) and "output" in result:
                        return result["output"]
                    elif isinstance(result, str):
                        return result
                    else:
                        return str(result)
                except Exception as e:
                    return f"Error: {str(e)}"
            
            def list_tools(self) -> List:
                """列出可用工具（兼容方法）"""
                return tools
        
        return AgentWrapper(agent_executor, agent_name)
    
    def _create_llm_chain_agent(
        self,
        system_prompt: str,
        agent_name: str
    ):
        """
        创建不使用工具的LLM Chain Agent（用于Planner Agent）
        
        问题：create_openai_tools_agent不支持空工具列表，会报错"[] is too short - 'tools'"
        解决方案：对于不需要工具的Agent，使用LLMChain直接调用LLM
        
        Args:
            system_prompt: 系统提示词
            agent_name: Agent名称
            
        Returns:
            带run方法的包装器（与Agent接口兼容）
        """
        # 创建提示词模板（不需要agent_scratchpad，因为没有工具）
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])
        
        # 使用现代方式：prompt | llm (RunnableSequence)
        # 避免使用已弃用的LLMChain
        chain = prompt | self.llm
        
        # 包装chain，添加run方法以保持接口兼容
        class LLMChainWrapper:
            """LLM Chain包装器，保持与Agent接口兼容"""
            def __init__(self, chain, name: str):
                self.chain = chain
                self.name = name
            
            def run(self, query: str) -> str:
                """运行LLM Chain，保持与SimpleAgent.run()接口兼容"""
                try:
                    # 使用invoke方法调用chain
                    result = self.chain.invoke({"input": query})
                    # 结果可能是AIMessage对象，需要提取content
                    if hasattr(result, 'content'):
                        return result.content
                    elif isinstance(result, dict) and "text" in result:
                        return result["text"]
                    elif isinstance(result, str):
                        return result
                    else:
                        return str(result)
                except Exception as e:
                    return f"Error: {str(e)}"
        
        return LLMChainWrapper(chain, agent_name)
    
    def plan_trip(self, request: TripRequest) -> TripPlan:
        """
        使用多智能体协作生成旅行计划

        Args:
            request: 旅行请求

        Returns:
            旅行计划
        """
        try:
            print(f"\n{'='*60}")
            print(f"🚀 Starting multi-agent collaborative trip planning...")
            print(f"Destination: {request.city}")
            print(f"Dates: {request.start_date} to {request.end_date}")
            print(f"Days: {request.travel_days} days")
            print(f"Preferences: {', '.join(request.preferences) if request.preferences else 'None'}")
            print(f"{'='*60}\n")

            # Step 1: Attraction search Agent searches for attractions
            print("📍 Step 1: Searching for attractions...")
            # Translate city name to Chinese for MCP tool compatibility
            chinese_city = translate_city_name(request.city)
            print(f"   🔄 City name translation: {request.city} -> {chinese_city}")
            attraction_query = self._build_attraction_query(request)
            # Update query to explicitly use Chinese city name for tool calls
            attraction_query = attraction_query.replace(
                f"in {request.city}",
                f"in {request.city} (use Chinese city name '{chinese_city}' when calling the tool)"
            )
            attraction_response = self.attraction_agent.run(attraction_query)
            print(f"Attraction search result: {attraction_response[:200]}...\n")

            # Step 2: Weather query Agent queries weather
            print("🌤️  Step 2: Querying weather...")
            # Translate city name to Chinese for weather API (requires Chinese city names)
            chinese_city = translate_city_name(request.city)
            weather_query = f"Get weather information for {chinese_city} (city name: {chinese_city}). Please use the amap_maps_weather tool with city='{chinese_city}'."
            weather_response = self.weather_agent.run(weather_query)
            print(f"Weather query result: {weather_response[:200]}...\n")

            # Step 3: Hotel recommendation Agent searches for hotels
            print("🏨 Step 3: Searching for hotels...")
            # Translate city name to Chinese for MCP tool compatibility
            chinese_city = translate_city_name(request.city)
            hotel_query = f"Search for {request.accommodation} hotels in {chinese_city} (city name: {chinese_city}). Please use the amap_maps_text_search tool with keywords='hotel' and city='{chinese_city}'."
            hotel_response = self.hotel_agent.run(hotel_query)
            print(f"Hotel search result: {hotel_response[:200]}...\n")

            # Step 4: Trip planning Agent integrates information to generate plan
            print("📋 Step 4: Generating trip plan...")
            planner_query = self._build_planner_query(request, attraction_response, weather_response, hotel_response)
            planner_response = self.planner_agent.run(planner_query)
            print(f"Trip planning result: {planner_response[:300]}...\n")

            # Parse final plan
            print(f"🔍 Starting to parse response, response length: {len(planner_response)} characters")
            trip_plan = self._parse_response(planner_response, request)
            
            # Debug: Print parsing results
            print(f"🔍 Parsing results:")
            print(f"   city: {trip_plan.city}")
            print(f"   days count: {len(trip_plan.days)}")
            print(f"   weather_info count: {len(trip_plan.weather_info)}")
            print(f"   overall_suggestions: {trip_plan.overall_suggestions[:100] if trip_plan.overall_suggestions else 'None'}...")

            print(f"{'='*60}")
            print(f"✅ Trip plan generation completed!")
            print(f"{'='*60}\n")

            return trip_plan

        except Exception as e:
            print(f"❌ Trip plan generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_plan(request)
    
    def _build_attraction_query(self, request: TripRequest) -> str:
        """
        Build attraction search query
        
        Modification notes:
        - LangChain version: Uses natural language query, Agent will automatically call tools
        - No longer needs [TOOL_CALL:...] format
        - Maintains interface compatibility (returns string)
        - Translates city name to Chinese for MCP tool compatibility
        """
        keywords = "attractions"
        if request.preferences:
            # Convert preferences to English keywords
            preference_map = {
                "历史文化": "historical culture",
                "自然风光": "natural scenery",
                "美食": "food",
                "购物": "shopping",
                "娱乐": "entertainment"
            }
            # Try to map, if not found use original value
            pref = request.preferences[0]
            keywords = preference_map.get(pref, pref)
        else:
            keywords = "attractions"

        # Translate city name to Chinese for MCP tool compatibility
        # Note: We use English city name in the query for LLM, but the tool will translate it
        # LangChain version: Uses natural language query, Agent will automatically identify and call tools
        query = f"Search for {keywords} in {request.city}. Please use the amap_maps_text_search tool to find attractions, restaurants, or other points of interest. Note: When calling the tool, use the Chinese city name if the city name is in English."
        return query

    def _build_planner_query(self, request: TripRequest, attractions: str, weather: str, hotels: str = "") -> str:
        """
        构建行程规划查询
        
        修改说明：
        - 改为英文版本
        - 保持接口兼容
        """
        preferences_str = ', '.join(request.preferences) if request.preferences else 'none'
        
        query = f"""Please generate a {request.travel_days}-day travel plan for {request.city} based on the following information:

**Basic Information:**
- City: {request.city}
- Dates: {request.start_date} to {request.end_date}
- Days: {request.travel_days} days
- Transportation: {request.transportation}
- Accommodation: {request.accommodation}
- Preferences: {preferences_str}

**Attraction Information:**
{attractions}

**Weather Information:**
{weather}

**Hotel Information:**
{hotels}

**Requirements:**
1. Arrange 2-3 attractions per day
2. Each day must include breakfast, lunch, and dinner
3. Recommend a specific hotel for each day (select from hotel information)
4. Consider the distance between attractions and transportation methods
5. Return complete JSON format data
6. Attraction coordinates (longitude, latitude) must be accurate and real
7. **CRITICAL: ALL output must be in ENGLISH** - Translate all Chinese text to English:
   - Attraction names, addresses, descriptions
   - Hotel names and addresses
   - Weather descriptions (e.g., "晴" -> "Sunny", "北风" -> "North wind")
   - All meal names and descriptions
   - All suggestions and text content
"""
        if request.free_text_input:
            query += f"\n**Additional Requirements:** {request.free_text_input}"

        return query
    
    def _parse_response(self, response: str, request: TripRequest) -> TripPlan:
        """
        解析Agent响应
        
        Args:
            response: Agent响应文本
            request: 原始请求
            
        Returns:
            旅行计划
        """
        try:
            # 尝试从响应中提取JSON
            # 查找JSON代码块
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response and "}" in response:
                # 直接查找JSON对象
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                raise ValueError("响应中未找到JSON数据")
            
            # Parse JSON
            print(f"🔍 Extracted JSON length: {len(json_str)} characters")
            print(f"🔍 JSON first 200 characters: {json_str[:200]}...")
            data = json.loads(json_str)
            print(f"🔍 JSON parsed successfully, keys: {list(data.keys())}")
            
            # Convert to TripPlan object
            print(f"🔍 Starting to create TripPlan object...")
            trip_plan = TripPlan(**data)
            print(f"🔍 TripPlan object created successfully")
            
            return trip_plan
            
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parsing failed: {str(e)}")
            print(f"   JSON string position: {e.pos}")
            print(f"   Will use fallback plan generation")
            return self._create_fallback_plan(request)
        except Exception as e:
            print(f"⚠️  Failed to parse response: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            print(f"   Detailed error:")
            traceback.print_exc()
            print(f"   Will use fallback plan generation")
            return self._create_fallback_plan(request)
    
    def _create_fallback_plan(self, request: TripRequest) -> TripPlan:
        """创建备用计划(当Agent失败时)"""
        from datetime import datetime, timedelta
        
        # 解析日期
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        
        # 创建每日行程
        days = []
        for i in range(request.travel_days):
            current_date = start_date + timedelta(days=i)
            
            day_plan = DayPlan(
                date=current_date.strftime("%Y-%m-%d"),
                day_index=i,
                description=f"Day {i+1} itinerary",
                transportation=request.transportation,
                accommodation=request.accommodation,
                attractions=[
                    Attraction(
                        name=f"{request.city} Attraction {j+1}",
                        address=f"{request.city}",
                        location=Location(longitude=116.4 + i*0.01 + j*0.005, latitude=39.9 + i*0.01 + j*0.005),
                        visit_duration=120,
                        description=f"Famous attraction in {request.city}",
                        category="Attraction"
                    )
                    for j in range(2)
                ],
                meals=[
                    Meal(type="breakfast", name=f"Day {i+1} Breakfast", description="Local specialty breakfast"),
                    Meal(type="lunch", name=f"Day {i+1} Lunch", description="Lunch recommendation"),
                    Meal(type="dinner", name=f"Day {i+1} Dinner", description="Dinner recommendation")
                ]
            )
            days.append(day_plan)
        
        return TripPlan(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            days=days,
            weather_info=[],
            overall_suggestions=f"This is a {request.travel_days}-day itinerary for {request.city}. Please check the opening hours of attractions in advance."
        )


# 全局多智能体系统实例
_multi_agent_planner = None


def get_trip_planner_agent() -> MultiAgentTripPlanner:
    """获取多智能体旅行规划系统实例(单例模式)"""
    global _multi_agent_planner

    if _multi_agent_planner is None:
        _multi_agent_planner = MultiAgentTripPlanner()

    return _multi_agent_planner

