<div align="right">

**中文** | [English](README.md)

</div>

# Trip Planner - Intelligent Travel Assistant 🌍✈️

基于 LangChain 框架构建的智能旅行规划助手，集成高德地图 MCP 服务，提供个性化的多日旅行计划生成。

> **📌 项目来源**: 本项目由 [HelloAgents](https://github.com/datawhalechina/Hello-Agents) 框架的旅行规划示例迁移而来，现已完全迁移到 LangChain 框架，并进行了功能增强和优化。

## ✨ 功能特点

- 🤖 **AI驱动的旅行规划**: 基于 LangChain 多智能体系统，智能生成详细的多日旅程
- 🗺️ **高德地图集成**: 通过 MCP 协议接入高德地图服务，支持景点搜索、路线规划、天气查询
- 🧠 **智能工具调用**: 多个专门的 Agent 自动调用高德地图 MCP 工具，获取实时 POI、路线和天气信息
- 🎨 **现代化前端**: Vue3 + TypeScript + Vite，响应式设计，流畅的用户体验
- 📱 **完整功能**: 包含住宿、交通、餐饮和景点游览时间推荐
- 🌐 **英文输出**: 所有提示词和输出均为英文，适合国际化使用

## 🏗️ 技术栈

### 后端
- **框架**: LangChain (AgentExecutor)
- **API**: FastAPI
- **MCP工具**: amap-mcp-server (高德地图)
- **LLM**: 支持多种 LLM 提供商 (OpenAI, DeepSeek 等)
- **MCP客户端**: 自定义 MCP 客户端实现

### 前端
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI组件库**: Ant Design Vue
- **地图服务**: 高德地图 JavaScript API
- **HTTP客户端**: Axios

## 📁 项目结构

```
trip-planner/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── agents/            # Agent实现
│   │   │   └── trip_planner_agent.py  # 多智能体旅行规划系统
│   │   ├── api/               # FastAPI路由
│   │   │   ├── main.py
│   │   │   └── routes/
│   │   │       ├── trip.py    # 旅行规划API
│   │   │       ├── poi.py     # POI搜索API
│   │   │       └── map.py     # 地图相关API
│   │   ├── services/          # 服务层
│   │   │   ├── amap_service.py      # 高德地图服务
│   │   │   ├── llm_service.py        # LLM服务
│   │   │   ├── mcp_client.py         # MCP客户端
│   │   │   ├── mcp_tools.py          # MCP工具封装
│   │   │   └── unsplash_service.py   # Unsplash图片服务
│   │   ├── models/            # 数据模型
│   │   │   └── schemas.py
│   │   ├── utils/             # 工具函数
│   │   │   └── city_translator.py    # 城市名称翻译
│   │   └── config.py          # 配置管理
│   ├── requirements.txt
│   └── run.py                 # 启动脚本
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── services/          # API服务
│   │   ├── types/             # TypeScript类型
│   │   └── views/             # 页面视图
│   │       ├── Home.vue       # 首页
│   │       └── Result.vue     # 结果页
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 🚀 快速开始

### 前提条件

- Python 3.10+ (必需，Pydantic 2.x 要求)
- Node.js 18+
- `uv` 工具 (用于运行 MCP 服务器)
- 高德地图 API 密钥 (Web 服务 API)
- LLM API 密钥 (OpenAI/DeepSeek 等)

### 安装 `uv` 工具

MCP 服务器需要 `uv` 工具来运行：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

重新加载 shell：
```bash
source ~/.zshrc  # 或 ~/.bashrc
```

验证安装：
```bash
uvx --version
```

### 后端安装

1. 进入后端目录
```bash
cd backend
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量

创建 `.env` 文件：
```bash
# LLM配置
LLM_API_KEY=your_llm_api_key_here
LLM_BASE_URL=https://api.openai.com/v1  # 或你的LLM提供商URL
LLM_MODEL_ID=gpt-4  # 或你的模型名称

# 高德地图配置
AMAP_MAPS_API_KEY=your_amap_api_key_here

# 服务器配置
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

5. 启动后端服务
```bash
python run.py
```

或者使用 uvicorn 直接启动：
```bash
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端安装

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 配置环境变量

创建 `.env` 文件：
```bash
# 高德地图Web API Key
VITE_AMAP_WEB_KEY=your_amap_web_key

# API基础URL (可选，默认 http://localhost:8000)
VITE_API_BASE_URL=http://localhost:8000
```

4. 启动开发服务器
```bash
npm run dev
```

5. 打开浏览器访问 `http://localhost:5173`

## 📝 使用指南

1. 在首页填写旅行信息:
   - 目的地城市 (支持中英文)
   - 旅行日期和天数
   - 交通方式偏好
   - 住宿偏好
   - 旅行风格标签

2. 点击"生成旅行计划"按钮

3. 系统将:
   - 调用多智能体系统生成初步计划
   - 景点搜索 Agent 自动调用高德地图 MCP 工具搜索景点
   - 天气查询 Agent 获取天气预报信息
   - 酒店推荐 Agent 搜索合适的住宿
   - 行程规划 Agent 整合所有信息生成完整行程

4. 查看结果:
   - 每日详细行程
   - 景点信息与地图标记
   - 交通路线规划
   - 天气预报
   - 餐饮推荐
   - 酒店推荐

## 🔧 核心实现

### LangChain 多智能体系统

系统包含 4 个专门的 Agent，使用 LangChain 的 `AgentExecutor` 实现：

1. **景点搜索 Agent** (`attraction_agent`): 搜索目的地景点和 POI
2. **天气查询 Agent** (`weather_agent`): 查询目的地天气预报
3. **酒店推荐 Agent** (`hotel_agent`): 搜索和推荐住宿
4. **行程规划 Agent** (`planner_agent`): 整合信息生成完整行程

```python
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate
from ..services.llm_service import get_llm
from ..services.mcp_tools import get_amap_tools

# 创建 Agent
llm = get_llm()
tools = get_amap_tools()
prompt = ChatPromptTemplate.from_messages([...])

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
```

### MCP 工具集成

系统通过自定义 MCP 客户端连接高德地图 MCP 服务器，支持以下工具：

- `amap_maps_text_search`: 搜索景点 POI
- `amap_maps_weather`: 查询天气
- `amap_maps_direction_walking_by_address`: 步行路线规划
- `amap_maps_direction_driving_by_address`: 驾车路线规划
- `amap_maps_direction_transit_integrated_by_address`: 公共交通路线规划

### 城市名称翻译

系统内置城市名称翻译功能，支持中英文城市名称自动转换，确保 MCP 工具调用时使用正确的中文城市名称。

## 📄 API 文档

启动后端服务后，访问以下地址查看完整的 API 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

主要端点:
- `POST /api/trip/plan` - 生成旅行计划
- `GET /api/poi/search` - 搜索 POI
- `GET /api/map/weather` - 查询天气
- `POST /api/map/route` - 规划路线

## 🧪 测试

后端提供了多个测试脚本：

```bash
cd backend

# 测试 LLM 服务
python test_llm_service.py

# 测试 MCP 工具
python test_mcp_tool.py

# 测试所有 Agent
python test_all_agents.py

# 端到端测试
python test_e2e.py
```

## 📦 部署

详细的部署指南请参考 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

## 🔄 项目迁移说明

### 从 HelloAgents 到 LangChain

本项目**原基于 HelloAgents 框架**开发，现已完全迁移到 LangChain 框架。迁移的主要原因是：

- 🎯 **框架生态**: LangChain 拥有更成熟的工具链和更丰富的社区支持
- 🔧 **灵活性**: LangChain 提供更灵活的 Agent 构建方式
- 📚 **文档完善**: LangChain 文档更加完善，便于维护和扩展
- 🌐 **国际化**: 迁移后所有输出改为英文，更适合国际化使用

### 主要变化

- ✅ 使用 LangChain 的 `AgentExecutor` 替代 HelloAgents 的 `SimpleAgent`
- ✅ 自定义 MCP 客户端实现，不再依赖 HelloAgents 的 `MCPTool`
- ✅ 所有提示词和输出改为英文
- ✅ 保持 API 接口完全兼容，前端无需修改
- ✅ 增强了错误处理和重试机制
- ✅ 优化了 Agent 之间的协作流程

### 原始项目参考

- [HelloAgents 教程](https://github.com/datawhalechina/Hello-Agents) - 原始框架和教程
- [HelloAgents 框架](https://github.com/jjyaoao/HelloAgents) - 原始框架实现

更多迁移详情请参考 [MIGRATION_PLAN.md](./MIGRATION_PLAN.md)

## 🤝 贡献指南

欢迎提交 Pull Request 或 Issue!

## 📜 开源协议

CC BY-NC-SA 4.0

## 🙏 致谢

- [HelloAgents](https://github.com/datawhalechina/Hello-Agents) - 原始项目框架和教程，本项目基于此迁移而来
- [HelloAgents 框架](https://github.com/jjyaoao/HelloAgents) - 原始智能体框架实现
- [LangChain](https://github.com/langchain-ai/langchain) - LLM 应用开发框架（当前使用）
- [高德地图开放平台](https://lbs.amap.com/) - 地图服务
- [amap-mcp-server](https://github.com/sugarforever/amap-mcp-server) - 高德地图 MCP 服务器
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架

---

**Trip Planner - Intelligent Travel Assistant** - 让旅行计划变得简单而智能 🌈
