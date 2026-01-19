<div align="right">

[中文](README.zh.md) | **English**

</div>

# Trip Planner - Intelligent Travel Assistant 🌍✈️

An intelligent trip planning assistant built on the LangChain framework, integrated with Amap (Gaode Map) MCP services, providing personalized multi-day travel plan generation.

> **📌 Project Origin**: This project was migrated from the [HelloAgents](https://github.com/datawhalechina/Hello-Agents) framework's trip planning example. It has been fully migrated to the LangChain framework with enhanced functionality and optimizations.

## ✨ Features

- 🤖 **AI-Powered Trip Planning**: Intelligent multi-day itinerary generation based on LangChain multi-agent system
- 🗺️ **Amap Integration**: Access to Amap services through MCP protocol, supporting attraction search, route planning, and weather queries
- 🧠 **Intelligent Tool Calling**: Specialized agents automatically call Amap MCP tools to obtain real-time POI, route, and weather information
- 🎨 **Modern Frontend**: Vue3 + TypeScript + Vite with responsive design and smooth user experience
- 📱 **Complete Features**: Includes accommodation, transportation, dining, and attraction visit time recommendations
- 🌐 **English Output**: All prompts and outputs are in English, suitable for international use

## 🏗️ Tech Stack

### Backend
- **Framework**: LangChain (AgentExecutor)
- **API**: FastAPI
- **MCP Tools**: amap-mcp-server (Amap/Gaode Map)
- **LLM**: Supports multiple LLM providers (OpenAI, DeepSeek, etc.)
- **MCP Client**: Custom MCP client implementation

### Frontend
- **Framework**: Vue 3 + TypeScript
- **Build Tool**: Vite
- **UI Library**: Ant Design Vue
- **Map Service**: Amap JavaScript API
- **HTTP Client**: Axios

## 📁 Project Structure

```
trip-planner/
├── backend/                    # Backend service
│   ├── app/
│   │   ├── agents/            # Agent implementations
│   │   │   └── trip_planner_agent.py  # Multi-agent trip planning system
│   │   ├── api/               # FastAPI routes
│   │   │   ├── main.py
│   │   │   └── routes/
│   │   │       ├── trip.py    # Trip planning API
│   │   │       ├── poi.py     # POI search API
│   │   │       └── map.py     # Map-related API
│   │   ├── services/          # Service layer
│   │   │   ├── amap_service.py      # Amap service
│   │   │   ├── llm_service.py        # LLM service
│   │   │   ├── mcp_client.py         # MCP client
│   │   │   ├── mcp_tools.py          # MCP tools wrapper
│   │   │   └── unsplash_service.py   # Unsplash image service
│   │   ├── models/            # Data models
│   │   │   └── schemas.py
│   │   ├── utils/             # Utility functions
│   │   │   └── city_translator.py    # City name translation
│   │   └── config.py          # Configuration management
│   ├── requirements.txt
│   └── run.py                 # Startup script
├── frontend/                   # Frontend application
│   ├── src/
│   │   ├── services/          # API services
│   │   ├── types/             # TypeScript types
│   │   └── views/             # Page views
│   │       ├── Home.vue       # Home page
│   │       └── Result.vue     # Results page
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+ (Required for Pydantic 2.x)
- Node.js 18+
- `uv` tool (for running MCP server)
- Amap API key (Web Service API)
- LLM API key (OpenAI/DeepSeek, etc.)

### Install `uv` Tool

The MCP server requires the `uv` tool to run:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Reload your shell:
```bash
source ~/.zshrc  # or ~/.bashrc
```

Verify installation:
```bash
uvx --version
```

### Backend Setup

1. Navigate to the backend directory
```bash
cd backend
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables

Create a `.env` file:
```bash
# LLM Configuration
LLM_API_KEY=your_llm_api_key_here
LLM_BASE_URL=https://api.openai.com/v1  # or your LLM provider URL
LLM_MODEL_ID=gpt-4  # or your model name

# Amap Configuration
AMAP_MAPS_API_KEY=your_amap_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

5. Start the backend service
```bash
python run.py
```

Or start directly with uvicorn:
```bash
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Navigate to the frontend directory
```bash
cd frontend
```

2. Install dependencies
```bash
npm install
```

3. Configure environment variables

Create a `.env` file:
```bash
# Amap Web API Key
VITE_AMAP_WEB_KEY=your_amap_web_key

# API Base URL (optional, default: http://localhost:8000)
VITE_API_BASE_URL=http://localhost:8000
```

4. Start the development server
```bash
npm run dev
```

5. Open your browser and visit `http://localhost:5173`

## 📝 Usage Guide

1. Fill in travel information on the home page:
   - Destination city (supports both Chinese and English)
   - Travel dates and duration
   - Transportation preferences
   - Accommodation preferences
   - Travel style tags

2. Click the "Generate Trip Plan" button

3. The system will:
   - Call the multi-agent system to generate an initial plan
   - Attraction search agent automatically calls Amap MCP tools to search for attractions
   - Weather query agent fetches weather forecast information
   - Hotel recommendation agent searches for suitable accommodations
   - Trip planning agent integrates all information to generate a complete itinerary

4. View results:
   - Daily detailed itinerary
   - Attraction information with map markers
   - Transportation route planning
   - Weather forecast
   - Dining recommendations
   - Hotel recommendations

## 🔧 Core Implementation

### LangChain Multi-Agent System

The system includes 4 specialized agents implemented using LangChain's `AgentExecutor`:

1. **Attraction Search Agent** (`attraction_agent`): Searches for destination attractions and POIs
2. **Weather Query Agent** (`weather_agent`): Queries destination weather forecasts
3. **Hotel Recommendation Agent** (`hotel_agent`): Searches and recommends accommodations
4. **Trip Planning Agent** (`planner_agent`): Integrates information to generate complete itineraries

```python
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate
from ..services.llm_service import get_llm
from ..services.mcp_tools import get_amap_tools

# Create Agent
llm = get_llm()
tools = get_amap_tools()
prompt = ChatPromptTemplate.from_messages([...])

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
```

### MCP Tool Integration

The system connects to the Amap MCP server through a custom MCP client, supporting the following tools:

- `amap_maps_text_search`: Search for attraction POIs
- `amap_maps_weather`: Query weather
- `amap_maps_direction_walking_by_address`: Walking route planning
- `amap_maps_direction_driving_by_address`: Driving route planning
- `amap_maps_direction_transit_integrated_by_address`: Public transit route planning

### City Name Translation

The system includes built-in city name translation functionality, supporting automatic conversion between Chinese and English city names, ensuring correct Chinese city names are used when calling MCP tools.

## 📄 API Documentation

After starting the backend service, visit the following addresses to view the complete API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Main endpoints:
- `POST /api/trip/plan` - Generate trip plan
- `GET /api/poi/search` - Search POI
- `GET /api/map/weather` - Query weather
- `POST /api/map/route` - Plan route

## 🧪 Testing

The backend provides multiple test scripts:

```bash
cd backend

# Test LLM service
python test_llm_service.py

# Test MCP tools
python test_mcp_tool.py

# Test all agents
python test_all_agents.py

# End-to-end test
python test_e2e.py
```

## 📦 Deployment

For detailed deployment instructions, please refer to [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

## 🔄 Project Migration Notes

### From HelloAgents to LangChain

This project was **originally developed based on the HelloAgents framework** and has been fully migrated to the LangChain framework. The main reasons for migration are:

- 🎯 **Framework Ecosystem**: LangChain has a more mature toolchain and richer community support
- 🔧 **Flexibility**: LangChain provides more flexible agent construction methods
- 📚 **Better Documentation**: LangChain documentation is more comprehensive, facilitating maintenance and extension
- 🌐 **Internationalization**: After migration, all outputs are in English, more suitable for international use

### Major Changes

- ✅ Replaced HelloAgents' `SimpleAgent` with LangChain's `AgentExecutor`
- ✅ Custom MCP client implementation, no longer dependent on HelloAgents' `MCPTool`
- ✅ All prompts and outputs changed to English
- ✅ Maintained complete API compatibility, frontend requires no modifications
- ✅ Enhanced error handling and retry mechanisms
- ✅ Optimized collaboration flow between agents

### Original Project References

- [HelloAgents Tutorial](https://github.com/datawhalechina/Hello-Agents) - Original framework and tutorial
- [HelloAgents Framework](https://github.com/jjyaoao/HelloAgents) - Original framework implementation

For more migration details, please refer to [MIGRATION_PLAN.md](./MIGRATION_PLAN.md)

## 🤝 Contributing

Pull requests and issues are welcome!

## 📜 License

CC BY-NC-SA 4.0

## 🙏 Acknowledgments

- [HelloAgents](https://github.com/datawhalechina/Hello-Agents) - Original project framework and tutorial, this project is migrated from it
- [HelloAgents Framework](https://github.com/jjyaoao/HelloAgents) - Original agent framework implementation
- [LangChain](https://github.com/langchain-ai/langchain) - LLM application development framework (currently used)
- [Amap Open Platform](https://lbs.amap.com/) - Map services
- [amap-mcp-server](https://github.com/sugarforever/amap-mcp-server) - Amap MCP server
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Vue.js](https://vuejs.org/) - Progressive JavaScript framework

---

**Trip Planner - Intelligent Travel Assistant** - Making trip planning simple and intelligent 🌈
