# MCP调用问题修复分析

## 🐛 发现的问题

### 问题1: MCP工具调用错误

**错误信息**:
```
Error calling MCP tool: 'dict' object has no attribute 'returncode'
```

**原因**:
- 代码中还在尝试访问`result.returncode`
- 但`result`现在是一个字典（来自MCP客户端的`call_tool`方法返回）
- 不是subprocess的结果对象

**位置**: `backend/app/services/mcp_tools.py` 第105行

**修复**:
- 移除对`result.returncode`的访问
- 直接处理字典格式的响应
- 检查`result`字典中的`content`、`text`或`error`字段

### 问题2: Planner Agent提示词问题

**错误信息**:
```
Error: 'Input to ChatPromptTemplate is missing variables {'\n  "city"'}'
```

**原因**:
- 提示词中包含JSON示例
- LangChain将JSON中的`{`和`}`误认为是模板变量
- 例如`{"city": "City Name"}`被解析为变量`\n  "city"`

**位置**: `backend/app/agents/trip_planner_agent.py` `PLANNER_AGENT_PROMPT`

**修复**:
- 转义JSON示例中的所有`{`为`{{`
- 转义JSON示例中的所有`}`为`}}`
- 这样LangChain就不会将其误认为是模板变量

## ✅ 修复方案

### 修复1: MCP工具响应处理

**修复前**:
```python
result = mcp_client.call_tool(...)
if result.returncode != 0:  # ❌ result是字典，没有returncode属性
    ...
```

**修复后**:
```python
result = mcp_client.call_tool(...)
# result是字典，直接处理
if "content" in result:
    content = result["content"]
    ...
elif "error" in result:
    ...
```

### 修复2: 提示词JSON转义

**修复前**:
```python
```json
{
  "city": "City Name",
  ...
}
```
```

**修复后**:
```python
```json
{{
  "city": "City Name",
  ...
}}
```
```

## 📊 预期效果

### 修复前
- ❌ MCP工具调用失败：`'dict' object has no attribute 'returncode'`
- ❌ Planner Agent失败：提示词变量错误

### 修复后
- ✅ MCP工具调用成功：正确处理字典响应
- ✅ Planner Agent成功：提示词正确解析

## 🎯 验证

修复后重新运行测试：
```bash
python3 test_all_agents.py
```

预期结果：
- ✅ MCP工具调用成功
- ✅ Planner Agent正常工作
- ✅ 所有测试通过
