# Issue Analysis: Default Values in Trip Plan Results

## Problem Description

The system is returning fallback plan default values instead of real search results:
- Attractions: "Beijing景点1", "Beijing景点2" (fallback values)
- Descriptions: "这是Beijing的著名景点" (fallback description)
- Weather: Likely missing or default
- Hotels: Likely missing or default

## Root Cause Analysis

### ✅ Test Results from `diagnose_issue.py`

#### 1. **MCP Tools Work, BUT City Name Translation is Required**

**POI Search Tool:**
- ✅ English city name "Beijing" → Returns results (but may be incorrect location)
- ✅ Chinese city name "北京" → Returns correct Beijing attractions
- ⚠️ **Issue**: English city name may return results from wrong city (e.g., Hong Kong attractions when searching "Beijing")

**Weather Tool:**
- ❌ English city name "Beijing" → `{"error": "No forecast data available"}`
- ✅ Chinese city name "北京" → Returns complete weather forecast data
- ⚠️ **Critical Issue**: Weather API **requires Chinese city names**

#### 2. **Agent Tool Calling Works**

- ✅ Agents are correctly calling MCP tools
- ✅ Tools are being invoked with correct parameters
- ⚠️ **Issue**: Tools are being called with English city names, which causes:
  - Weather queries to fail
  - POI searches to return incorrect or no results

#### 3. **Why Fallback Plan is Triggered**

The fallback plan is created when:
1. Agent response parsing fails (JSON parsing error)
2. Exception occurs during trip planning
3. Agent returns empty or invalid results

**Current Flow:**
1. User sends request with English city name "Beijing"
2. Agent builds query: "Search for historical culture in Beijing"
3. Agent calls `amap_maps_text_search` with `city="Beijing"`
4. Tool may return incorrect results or no results
5. Weather agent calls `amap_maps_weather` with `city="Beijing"`
6. Weather tool returns error: "No forecast data available"
7. Planner agent receives incomplete/invalid data
8. JSON parsing fails or returns invalid structure
9. System falls back to `_create_fallback_plan()`

## Key Findings

### 🔴 Critical Issue: City Name Translation Missing

**Problem:**
- Frontend sends English city names (e.g., "Beijing", "Shanghai")
- MCP tools (especially weather API) require Chinese city names (e.g., "北京", "上海")
- No translation layer exists between frontend and MCP tools

**Evidence:**
```
Weather Tool Test:
- "Beijing" → {"error": "No forecast data available"}
- "北京" → Complete weather forecast data
```

### 🟡 Secondary Issue: POI Search Accuracy

**Problem:**
- POI search with English city names may return results from wrong cities
- Example: Searching "Beijing" returned Hong Kong attractions

**Evidence:**
```
POI Search Test:
- "Beijing" → Returned "Peak Tram Historical Gallery" (Hong Kong)
- "北京" → Returned correct Beijing attractions
```

## Solution Required

### 1. **Add City Name Translation**

Create a city name translation function that converts:
- English → Chinese: "Beijing" → "北京"
- Handle common cities: Beijing, Shanghai, Guangzhou, Shenzhen, etc.

### 2. **Update Tool Calls**

Modify `_build_attraction_query`, weather queries, and hotel queries to:
1. Translate city name from English to Chinese
2. Use Chinese city name when calling MCP tools
3. Keep English city name in user-facing responses

### 3. **Update MCP Tools (Optional)**

Alternatively, update MCP tools to:
- Accept both English and Chinese city names
- Handle translation internally

## Files That Need Changes

1. **`backend/app/agents/trip_planner_agent.py`**
   - Add city name translation function
   - Update `_build_attraction_query()` to translate city name
   - Update weather query to translate city name
   - Update hotel query to translate city name

2. **`backend/app/services/mcp_tools.py`** (Optional)
   - Add city name translation in tool `_run()` methods
   - Or document that tools require Chinese city names

## Impact

- **High**: Weather information will always fail with English city names
- **Medium**: POI searches may return incorrect results
- **Low**: Hotel searches may be affected

## Next Steps

1. ✅ **Diagnosis Complete** - Issue identified
2. ⏳ **Add City Name Translation** - Create translation function
3. ⏳ **Update Agent Queries** - Use translated city names for MCP calls
4. ⏳ **Test** - Verify weather and POI searches work correctly
5. ⏳ **Verify** - Ensure fallback plan is no longer triggered

---

**Date:** 2025-01-XX  
**Status:** 🔴 Issue Identified - City Name Translation Required
