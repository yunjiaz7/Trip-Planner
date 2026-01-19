# MCP 工具封装说明

## 🤔 什么是 MCP 工具封装？

### 当前版本（HelloAgents）的情况

**原来的代码已经有 MCP 工具封装了！**

看这段代码：
```python
# backend/app/agents/trip_planner_agent.py (第168-174行)
self.amap_tool = MCPTool(
    name="amap",
    description="高德地图服务",
    server_command=["uvx", "amap-mcp-server"],
    env={"AMAP_MAPS_API_KEY": settings.amap_api_key},
    auto_expand=True  # 关键：自动展开为多个工具
)

# 然后直接添加到Agent
self.attraction_agent.add_tool(self.amap_tool)
```

**HelloAgents 的 MCPTool 做了什么：**
1. ✅ 它已经封装了 MCP 协议
2. ✅ `auto_expand=True` 会自动将 MCP 服务器提供的所有工具展开
3. ✅ 例如：`amap-mcp-server` 提供多个工具：
   - `amap_maps_text_search` (搜索POI)
   - `amap_maps_weather` (查询天气)
   - `amap_maps_direction_walking_by_address` (步行路线)
   - 等等...
4. ✅ `SimpleAgent` 可以直接使用这个 `MCPTool`

---

## ❓ 为什么迁移到 LangChain 需要重新封装？

### 问题：框架不兼容

**HelloAgents 的 MCPTool ≠ LangChain 的 Tool**

```
HelloAgents 框架:
  SimpleAgent
    └── MCPTool (HelloAgents专用)
         └── 自动处理MCP协议
              └── 展开为多个工具

LangChain 框架:
  AgentExecutor
    └── 需要 BaseTool (LangChain标准)
         └── 不认识 HelloAgents 的 MCPTool ❌
```

### 具体原因

1. **类型不兼容**
   - LangChain 的 `AgentExecutor` 期望的工具类型是：`List[BaseTool]`
   - HelloAgents 的 `MCPTool` 不是 `BaseTool` 的子类
   - 直接使用会报错：`TypeError: tool must be an instance of BaseTool`

2. **接口不同**
   - HelloAgents: `agent.add_tool(mcp_tool)` 
   - LangChain: `AgentExecutor(agent=agent, tools=[tool1, tool2, ...])`
   - LangChain 需要工具列表，而不是单个 MCPTool 对象

3. **工具调用方式不同**
   - HelloAgents: 使用自定义格式 `[TOOL_CALL:tool_name:params]`
   - LangChain: 使用标准的 Tool Calling（OpenAI Function Calling）
   - LangChain 需要每个工具都是独立的 `BaseTool` 实例

---

## 🔧 解决方案：重新封装为 LangChain Tool

### 需要做什么？

**将 MCP 服务器的每个工具封装为独立的 LangChain Tool**

```
原来（HelloAgents）:
  MCPTool (一个对象)
    └── auto_expand=True
         └── 内部自动展开为多个工具

迁移后（LangChain）:
  AmapTextSearchTool (BaseTool)
  AmapWeatherTool (BaseTool)
  AmapDirectionTool (BaseTool)
  ... (每个工具都是独立的 BaseTool 实例)
```

### 封装示例

```python
from langchain.tools import BaseTool
from typing import Optional
import subprocess
import json

class AmapTextSearchTool(BaseTool):
    """高德地图POI搜索工具 - LangChain版本"""
    name = "amap_maps_text_search"
    description = "Search for POIs in Amap. Use this to find attractions, restaurants, hotels."
    
    def _run(self, keywords: str, city: str, citylimit: str = "true") -> str:
        """
        调用MCP服务器搜索POI
        
        这里需要：
        1. 通过某种方式调用 MCP 服务器（subprocess/HTTP/SDK）
        2. 传递参数给 MCP 服务器
        3. 返回结果
        """
        # 方案1: 通过subprocess调用uvx amap-mcp-server
        # 方案2: 使用MCP Python SDK（如果有）
        # 方案3: HTTP调用（如果MCP服务器提供HTTP接口）
        ...
    
    async def _arun(self, keywords: str, city: str, citylimit: str = "true") -> str:
        """异步版本"""
        ...
```

---

## 📊 对比说明

### HelloAgents 版本（当前）

```python
# 1. 创建一个MCPTool（自动封装）
amap_tool = MCPTool(
    name="amap",
    server_command=["uvx", "amap-mcp-server"],
    env={"AMAP_MAPS_API_KEY": "xxx"},
    auto_expand=True  # 自动展开
)

# 2. 直接添加到Agent
agent = SimpleAgent(...)
agent.add_tool(amap_tool)  # 一个对象，内部包含多个工具

# 3. Agent自动识别工具
# HelloAgents会自动处理工具调用
```

**优点：**
- ✅ 简单：一个对象搞定所有工具
- ✅ 自动：`auto_expand=True` 自动展开
- ✅ 框架处理：HelloAgents自动处理MCP协议

**缺点：**
- ❌ 只能在HelloAgents框架中使用
- ❌ 不能直接用于LangChain

---

### LangChain 版本（迁移后）

```python
# 1. 需要手动封装每个工具
class AmapTextSearchTool(BaseTool):
    name = "amap_maps_text_search"
    description = "..."
    def _run(self, keywords: str, city: str) -> str:
        # 手动调用MCP服务器
        ...

class AmapWeatherTool(BaseTool):
    name = "amap_maps_weather"
    description = "..."
    def _run(self, city: str) -> str:
        # 手动调用MCP服务器
        ...

# 2. 创建工具列表
tools = [
    AmapTextSearchTool(),
    AmapWeatherTool(),
    # ... 其他工具
]

# 3. 传递给AgentExecutor
agent = AgentExecutor(agent=agent, tools=tools)
```

**优点：**
- ✅ 标准：使用LangChain标准接口
- ✅ 灵活：可以自定义每个工具的行为
- ✅ 兼容：可以在任何LangChain应用中使用

**缺点：**
- ❌ 需要手动封装每个工具
- ❌ 需要手动处理MCP协议调用
- ❌ 工作量较大（需要封装3-5个工具）

---

## 🎯 关键问题：如何调用 MCP 服务器？

### 当前 HelloAgents 的做法

HelloAgents 的 `MCPTool` 内部已经处理了：
1. 启动 MCP 服务器进程（`uvx amap-mcp-server`）
2. 通过 MCP 协议通信
3. 获取工具列表
4. 调用工具并返回结果

### 迁移后需要手动实现

**方案1：通过 subprocess 调用（推荐）**
```python
import subprocess
import json

def call_mcp_tool(tool_name: str, arguments: dict) -> str:
    """通过subprocess调用MCP服务器"""
    # 调用 uvx amap-mcp-server
    # 传递工具名和参数
    # 返回结果
    result = subprocess.run(
        ["uvx", "amap-mcp-server", "call", tool_name],
        input=json.dumps(arguments),
        capture_output=True,
        text=True
    )
    return result.stdout
```

**方案2：使用 MCP Python SDK（如果有）**
```python
from mcp import Client

client = Client("amap-mcp-server")
result = client.call_tool("amap_maps_text_search", {"keywords": "景点", "city": "北京"})
```

**方案3：HTTP 调用（如果MCP服务器提供HTTP接口）**
```python
import httpx

async def call_mcp_tool(tool_name: str, arguments: dict) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/mcp/call",
            json={"tool": tool_name, "arguments": arguments}
        )
        return response.text
```

---

## 📝 总结

### 为什么需要"MCP工具封装"？

1. **框架不兼容**
   - HelloAgents 的 `MCPTool` 不能在 LangChain 中直接使用
   - 需要转换为 LangChain 的 `BaseTool` 格式

2. **接口不同**
   - HelloAgents: 一个 `MCPTool` 对象（内部自动展开）
   - LangChain: 多个独立的 `BaseTool` 对象（需要手动创建）

3. **调用方式不同**
   - HelloAgents: 框架自动处理 MCP 协议
   - LangChain: 需要手动实现 MCP 协议调用

### 工作量评估

- **封装3-5个主要工具**：1-2天
- **测试工具调用**：0.5天
- **调试和优化**：0.5天

**总计：约2-3天**

### 关键挑战

⚠️ **如何调用 MCP 服务器？**
- 需要研究 MCP 协议的具体调用方式
- 可能需要查看 `hello-agents` 的源码了解 `MCPTool` 的实现
- 或者直接通过 subprocess 调用 `uvx amap-mcp-server`

---

## 💡 建议

在开始迁移前，建议：

1. **研究 HelloAgents 的 MCPTool 源码**
   - 了解它如何调用 MCP 服务器
   - 了解 MCP 协议的具体格式

2. **测试 MCP 服务器**
   - 手动运行 `uvx amap-mcp-server` 看看输出
   - 了解如何通过命令行调用工具

3. **先实现一个工具**
   - 先封装 `AmapTextSearchTool`
   - 测试是否能正常工作
   - 再批量封装其他工具
